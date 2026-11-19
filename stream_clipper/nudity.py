"""Поиск обнажённого тела в кадре (ягодицы, грудь, половые органы — и у игровых персонажей тоже).

Модель — открытая NudeNet (детектор YOLOv8, ~12 МБ). Скачивается один раз с PyPI (из пакета nudenet берём
только файл модели) и запускается через OpenCV — без тяжёлых библиотек. Работает без интернета и без Claude.
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import urllib.request
import zipfile

import numpy as np

from . import paths

LABELS = ["FEMALE_GENITALIA_COVERED", "FACE_FEMALE", "BUTTOCKS_EXPOSED", "FEMALE_BREAST_EXPOSED",
          "FEMALE_GENITALIA_EXPOSED", "MALE_BREAST_EXPOSED", "ANUS_EXPOSED", "FEET_EXPOSED", "BELLY_COVERED",
          "FEET_COVERED", "ARMPITS_COVERED", "ARMPITS_EXPOSED", "FACE_MALE", "BELLY_EXPOSED",
          "MALE_GENITALIA_EXPOSED", "ANUS_COVERED", "FEMALE_BREAST_COVERED", "BUTTOCKS_COVERED"]
# что площадки считают обнажёнкой (и за что режут показы / удаляют)
BAD = {"BUTTOCKS_EXPOSED": "голые ягодицы", "FEMALE_BREAST_EXPOSED": "голая грудь",
       "FEMALE_GENITALIA_EXPOSED": "половые органы", "MALE_GENITALIA_EXPOSED": "половые органы",
       "ANUS_EXPOSED": "половые органы"}
# пороги ниже обычных: игровая графика для модели «непривычна», уверенность у неё ниже, чем на фото.
# Лишнее срабатывание не страшно — в окне исправления галочку можно снять.
MIN_SCORE = {"BUTTOCKS_EXPOSED": 0.3, "FEMALE_BREAST_EXPOSED": 0.3}
DEFAULT_MIN = 0.35
SIZE = 320
_net = None


def model_path() -> str:
    return os.path.join(paths.default_work_dir(), "models", "nudenet_320n.onnx")


def ensure_model(log=print) -> str | None:
    p = model_path()
    if os.path.exists(p) and os.path.getsize(p) > 1_000_000:
        return p
    os.makedirs(os.path.dirname(p), exist_ok=True)
    log("Скачиваю модель поиска обнажёнки (~12 МБ, один раз)...")
    try:
        with urllib.request.urlopen("https://pypi.org/pypi/nudenet/3.4.2/json", timeout=30) as r:
            info = json.load(r)
        url = next(u["url"] for u in info["urls"] if u["filename"].endswith(".whl"))
        with urllib.request.urlopen(url, timeout=120) as r:
            data = r.read()
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            name = next(n for n in z.namelist() if n.endswith("320n.onnx"))
            blob = z.read(name)
    except Exception as e:
        try:  # запасной адрес — релиз на GitHub
            with urllib.request.urlopen(
                    "https://github.com/notAI-tech/NudeNet/releases/download/v3.4-weights/320n.onnx", timeout=120) as r:
                blob = r.read()
        except Exception:
            log(f"Не удалось скачать модель поиска обнажёнки: {e}")
            return None
    with open(p + ".part", "wb") as f:
        f.write(blob)
    os.replace(p + ".part", p)
    return p


# ---------- подготовка модели под OpenCV ----------
# В исходной модели размер картинки «плавающий», а последний блок (сетка якорей) считается на лету — OpenCV так
# не умеет. Поэтому режем модель перед этим блоком (три выхода «сырых» свёрток) и фиксируем вход 1x3x320x320;
# остаток (DFL-декодирование рамок) делаем сами в numpy. Правим файл модели напрямую (формат protobuf),
# чтобы не ставить лишних пакетов.
HEADS = ["/model.22/Concat_output_0", "/model.22/Concat_1_output_0", "/model.22/Concat_2_output_0"]
STRIDES = [8, 16, 32]


def _varint(buf: bytes, i: int):
    v = shift = 0
    while True:
        b = buf[i]
        i += 1
        v |= (b & 0x7F) << shift
        if b < 0x80:
            return v, i
        shift += 7


def _enc_varint(v: int) -> bytes:
    out = bytearray()
    while True:
        b = v & 0x7F
        v >>= 7
        out.append(b | (0x80 if v else 0))
        if not v:
            return bytes(out)


def _fields(buf: bytes):
    """[(номер поля, тип, значение, исходные байты поля)]."""
    i, out = 0, []
    while i < len(buf):
        start = i
        key, i = _varint(buf, i)
        f, wt = key >> 3, key & 7
        if wt == 0:
            v, i = _varint(buf, i)
        elif wt == 1:
            v, i = buf[i:i + 8], i + 8
        elif wt == 5:
            v, i = buf[i:i + 4], i + 4
        elif wt == 2:
            n, i = _varint(buf, i)
            v, i = buf[i:i + n], i + n
        else:
            raise ValueError("protobuf: неизвестный тип поля")
        out.append((f, wt, v, buf[start:i]))
    return out


def _ld(field: int, payload: bytes) -> bytes:
    return _enc_varint(field << 3 | 2) + _enc_varint(len(payload)) + payload


def _vi(field: int, value: int) -> bytes:
    return _enc_varint(field << 3) + _enc_varint(value)


def _value_info(name: str, dims: list[int] | None) -> bytes:
    tensor = _vi(1, 1)  # float
    if dims:
        tensor += _ld(2, b"".join(_ld(1, _vi(1, d)) for d in dims))
    return _ld(1, name.encode()) + _ld(2, _ld(1, tensor))


def _strings(buf: bytes, field: int) -> list[str]:
    return [v.decode() for f, wt, v, _ in _fields(buf) if f == field and wt == 2]


def prepare_for_opencv(src: str, dst: str) -> None:
    data = open(src, "rb").read()
    model = _fields(data)
    graph = next(v for f, wt, v, _ in model if f == 7)
    g = _fields(graph)
    nodes = [(raw, _strings(v, 1), _strings(v, 2)) for f, wt, v, raw in g if f == 1]
    need, keep = set(HEADS), []
    for raw, ins, outs in reversed(nodes):  # нужны только узлы, от которых зависят три выхода
        if need & set(outs):
            keep.append(raw)
            need.update(ins)
    keep.reverse()
    new = bytearray()
    for f, wt, v, raw in g:
        if f == 1 or f in (11, 12, 13):
            continue
        if f == 5 and _strings(v, 8) and _strings(v, 8)[0] not in need:
            continue  # веса, которые больше не нужны
        new += raw
    new += b"".join(keep)
    new += _ld(11, _value_info("images", [1, 3, SIZE, SIZE]))
    for h, stride in zip(HEADS, STRIDES):
        new += _ld(12, _value_info(h, [1, 64 + len(LABELS), SIZE // stride, SIZE // stride]))
    out = bytearray()
    for f, wt, v, raw in model:
        out += _ld(7, bytes(new)) if f == 7 else raw
    with open(dst, "wb") as fh:
        fh.write(out)


def _get_net(log=print):
    global _net
    if _net is None:
        import cv2
        p = ensure_model(log)
        if not p:
            return None
        cv_path = p.replace(".onnx", "_cv2.onnx")
        if not os.path.exists(cv_path):
            prepare_for_opencv(p, cv_path)
        _net = cv2.dnn.readNetFromONNX(cv_path)
    return _net


def _decode(outs: list) -> np.ndarray:
    """Три «сырых» выхода → (кандидаты, 4 + классы): рамка cx, cy, w, h в пикселях входа 320 и вероятности."""
    res = []
    for o, stride in zip(outs, STRIDES):
        o = o[0]  # (64 + классы, H, W)
        _, h, w = o.shape
        box, cls = o[:64].reshape(4, 16, h * w), o[64:].reshape(-1, h * w)
        e = np.exp(box - box.max(axis=1, keepdims=True))
        dist = (e / e.sum(axis=1, keepdims=True) * np.arange(16).reshape(1, 16, 1)).sum(axis=1)  # (4, HW)
        gy, gx = np.mgrid[0:h, 0:w]
        ax, ay = gx.reshape(-1) + 0.5, gy.reshape(-1) + 0.5
        x1, y1, x2, y2 = ax - dist[0], ay - dist[1], ax + dist[2], ay + dist[3]
        xywh = np.stack([(x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1]) * stride
        res.append(np.concatenate([xywh, 1 / (1 + np.exp(-cls))], axis=0))
    return np.concatenate(res, axis=1).T


def _detect_square(net, img: np.ndarray, ox: int, oy: int) -> tuple[list, list, list]:
    """Одна квадратная часть кадра → рамки (в координатах всего кадра), вероятности, классы."""
    import cv2
    h, w = img.shape[:2]
    side = max(h, w)
    square = cv2.copyMakeBorder(img, 0, side - h, 0, side - w, cv2.BORDER_CONSTANT)
    blob = cv2.dnn.blobFromImage(square, 1 / 255.0, (SIZE, SIZE), swapRB=True, crop=False)
    net.setInput(blob)
    out = _decode(net.forward(HEADS))  # (кандидаты, 4 + классы)
    scale = side / SIZE
    boxes, scores, ids = [], [], []
    for row in out:
        cls = row[4:]
        k = int(np.argmax(cls))
        sc = float(cls[k])
        if sc < 0.15:
            continue
        cx, cy, bw, bh = (float(v) * scale for v in row[:4])
        x, y = max(0.0, cx - bw / 2), max(0.0, cy - bh / 2)
        boxes.append([ox + x, oy + y, min(bw, w - x), min(bh, h - y)])
        scores.append(sc)
        ids.append(k)
    return boxes, scores, ids


def tiles(w: int, h: int) -> list[tuple[int, int, int]]:
    """Квадраты, которыми просматриваем кадр: весь кадр + крупные квадраты по длинной стороне + мелкие 2x2 в каждом.
    Вертикальный клип 1080x1920 целиком сжимается в 320 px — человек в кадре игры выходит крошечным и теряется."""
    side = min(w, h)
    out = []
    long_ = max(w, h)
    for off in sorted({0, (long_ - side) // 2, long_ - side}):
        x, y = (0, off) if h >= w else (off, 0)
        out.append((x, y, side))
        half = side // 2
        for dx in (0, half):  # мелкие квадраты (крупные квадраты сами перекрываются)
            for dy in (0, half):
                out.append((x + dx, y + dy, half))
    return list(dict.fromkeys(out))


def detect_frame(frame: np.ndarray, log=print, fine: bool = True) -> list[dict]:
    """fine=False — только крупные квадраты (быстро), True — ещё и мелкие (видны далёкие/маленькие фигуры)."""
    """Кадр BGR → [{'label', 'score', 'box': (x, y, w, h) в пикселях}]."""
    import cv2
    net = _get_net(log)
    if net is None:
        return []
    h, w = frame.shape[:2]
    boxes, scores, ids = [], [], []
    for x, y, side in [t for t in tiles(w, h) if fine or t[2] >= min(w, h)]:
        b, sc, k = _detect_square(net, frame[y:y + side, x:x + side], x, y)
        boxes += b
        scores += sc
        ids += k
    res = []
    for i in cv2.dnn.NMSBoxes(boxes, scores, 0.15, 0.45) if boxes else []:
        i = int(np.array(i).flatten()[0])
        res.append({"label": LABELS[ids[i]], "score": scores[i], "box": tuple(int(v) for v in boxes[i])})
    return res


def _iou(a, b) -> float:
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def _near(a, b) -> bool:
    """Та же область на соседнем кадре: рамки пересекаются или центры близко (человек сдвинулся)."""
    if _iou(a, b) > 0.05:
        return True
    ca, cb = ((a[0] + a[2]) / 2, (a[1] + a[3]) / 2), ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
    return abs(ca[0] - cb[0]) < 0.12 and abs(ca[1] - cb[1]) < 0.08


def scan_clip(clip: str, every: float = 0.5, log=print) -> list[dict]:
    """Проходит по клипу каждые every секунд. Возвращает куски с обнажёнкой:
    [{'t0', 't1', 'box': [x, y, w, h] доли кадра, 'what'}].
    Против ложных срабатываний: рамка не больше ~1/5 кадра, и то же место должно найтись хотя бы на двух
    соседних проверках (случайная «вспышка» на одном кадре не считается)."""
    import cv2
    if _get_net(log) is None:
        return []
    cap = cv2.VideoCapture(clip)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    step = max(1, int(round(fps * every)))
    samples: list[tuple[float, list]] = []  # (время, [(x0, y0, x1, y1, что, уверенность)])
    idx = 0
    while True:
        ok = cap.grab()
        if not ok:
            break
        if idx % step == 0:
            ok, frame = cap.retrieve()
            if ok:
                H, W = frame.shape[:2]
                fine = (idx // step) % 2 == 0  # мелкие квадраты — раз в секунду, крупные — каждые полсекунды
                found = []
                for d in detect_frame(frame, log, fine=fine):
                    if d["label"] not in BAD or d["score"] < MIN_SCORE.get(d["label"], DEFAULT_MIN):
                        continue
                    x, y, w, h = d["box"]
                    if w * h > 0.2 * W * H or w > 0.6 * W or h > 0.45 * H:
                        continue  # «обнажёнка» на полэкрана — почти всегда ошибка модели
                    found.append((x / W, y / H, (x + w) / W, (y + h) / H, BAD[d["label"]], d["score"]))
                samples.append((idx / fps, found))
        idx += 1
        if total and idx > total + 5:
            break
    cap.release()
    # подтверждение: рядом (±1 проверка) должно быть похожее попадание; очень уверенные (≥0.6) — сразу
    hits = []
    for i, (t, found) in enumerate(samples):
        neigh = [b for j in (i - 1, i + 1) if 0 <= j < len(samples) for b in samples[j][1]]
        for b in found:
            if b[5] >= 0.6 or any(_near(b, n) for n in neigh):
                hits.append((t, b))
    # куски: подряд идущие попадания по одному месту; у каждого куска своя тесная рамка (≤ 1.5 с)
    spans: list[dict] = []
    for t, b in sorted(hits, key=lambda h: h[0]):
        box = b[:4]
        s = next((s for s in reversed(spans) if t - s["_last"] <= every * 2.5 and t - s["_first"] <= 1.5
                  and _near(s["b"], box)), None)
        if s:
            s["_last"] = t
            s["b"] = [min(s["b"][0], box[0]), min(s["b"][1], box[1]), max(s["b"][2], box[2]), max(s["b"][3], box[3])]
            s["what"].add(b[4])
        else:
            spans.append({"_first": t, "_last": t, "b": list(box), "what": {b[4]}})
    out = []
    for s in spans:
        x0, y0, x1, y1 = s["b"]
        out.append({"t0": max(0.0, s["_first"] - every * 0.6), "t1": s["_last"] + every * 0.6,
                    "box": [x0, y0, x1 - x0, y1 - y0], "what": ", ".join(sorted(s["what"]))})
    return out
