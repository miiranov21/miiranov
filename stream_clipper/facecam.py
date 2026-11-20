"""Поиск вебки стримера на кадре + память по стримерам + ручная рамка из окна программы."""
from __future__ import annotations

import json
import os
import urllib.request

from . import paths

YUNET_URLS = [
    "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/"
    "face_detection_yunet_2023mar.onnx",
    "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
]
_detector = None


# ---------- память по стримерам ----------
def _store_path() -> str:
    return os.path.join(paths.default_work_dir(), "facecams.json")


def load_store() -> dict:
    try:
        with open(_store_path(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_store(data: dict) -> None:
    os.makedirs(os.path.dirname(_store_path()), exist_ok=True)
    with open(_store_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def set_manual(channel: str, region: tuple | None, no_cam: bool = False) -> None:
    """Рамку вебки указали вручную (или «у стримера нет вебки»). region=None и no_cam=False — снова автоматически."""
    data = load_store()
    key = channel.lower()
    if region is None and not no_cam:
        data.pop(key, None)
    else:
        data[key] = {"manual": True, "none": no_cam, "region": list(region) if region else None}
    _save_store(data)


def get_entry(channel: str) -> dict:
    return load_store().get(channel.lower(), {})


def frame_path(channel: str) -> str:
    """Кадр из стрима (горизонтальный) — по нему в окне рисуют рамку вебки."""
    d = os.path.join(paths.default_work_dir(), "frames")
    os.makedirs(d, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in channel.lower()) or "stream"
    return os.path.join(d, safe + ".png")


def resolve(channel: str, segment: str, log=print):
    """Где вебка в этом клипе: ручная рамка > найденная сейчас > запомненная раньше. None — вебки нет."""
    entry = get_entry(channel) if channel else {}
    _save_frame(segment, channel)
    if entry.get("manual"):
        return None if entry.get("none") else tuple(entry["region"])
    found = detect_facecam(segment, log=log)
    if found and channel:
        data = load_store()
        old = data.get(channel.lower(), {}).get("region")
        # сглаживаем: вебка у стримера обычно на одном месте
        region = [round((a + b) / 2, 4) for a, b in zip(old, found)] if old and _close(old, found) else list(found)
        data[channel.lower()] = {"manual": False, "none": False, "region": region}
        _save_store(data)
        return tuple(region)
    if not found and entry.get("region"):
        log("    вебка в этом клипе не видна — беру запомненное место")
        return tuple(entry["region"])
    return found


def _close(a, b, tol: float = 0.08) -> bool:
    return abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol


def _save_frame(segment: str, channel: str) -> None:
    if not channel:
        return
    try:
        import cv2
        cap = cv2.VideoCapture(segment)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, int(total * 0.4)))
        ok, frame = cap.read()
        cap.release()
        if ok:
            h, w = frame.shape[:2]
            frame = cv2.resize(frame, (960, int(960 * h / w)))
            cv2.imwrite(frame_path(channel), frame)
    except Exception:
        pass


# ---------- поиск лица ----------
def _yunet():
    """Точный детектор лиц YuNet (модель 230 КБ скачивается один раз). None — не получилось."""
    global _detector
    if _detector is not None:
        return _detector or None
    try:
        import cv2
        model = os.path.join(paths.default_work_dir(), "yunet.onnx")
        if not os.path.exists(model) or os.path.getsize(model) < 100_000:
            os.makedirs(os.path.dirname(model), exist_ok=True)
            for url in YUNET_URLS:
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "stream-clipper"})
                    with urllib.request.urlopen(req, timeout=30) as r:
                        data = r.read()
                    if len(data) > 100_000:
                        with open(model, "wb") as f:
                            f.write(data)
                        break
                except Exception:
                    continue
        _detector = cv2.FaceDetectorYN.create(model, "", (320, 320), 0.6, 0.3, 5000)
    except Exception:
        _detector = False
    return _detector or None


def _faces(frame, W, H):
    """Лица на кадре: [(x, y, w, h)] в долях кадра."""
    import cv2
    det = _yunet()
    if det is not None:
        scale = 1280 / W if W > 1280 else 1.0  # уменьшаем для скорости
        img = cv2.resize(frame, (int(W * scale), int(H * scale))) if scale != 1.0 else frame
        det.setInputSize((img.shape[1], img.shape[0]))
        _, res = det.detect(img)
        if res is None:
            return []
        w_, h_ = img.shape[1], img.shape[0]
        return [(float(f[0]) / w_, float(f[1]) / h_, float(f[2]) / w_, float(f[3]) / h_) for f in res]
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=5, minSize=(int(H * 0.035),) * 2)
    return [(x / W, y / H, w / W, h / H) for (x, y, w, h) in faces]


def detect_facecam(video: str, samples: int = 20, cam_aspect: float = 1080 / 672, log=print):
    """(x, y, w, h) области вебки в долях кадра или None.
    Ищем лицо, которое в большинстве кадров стоит на одном месте (оверлей вебки),
    а не лица персонажей игры, которые двигаются."""
    try:
        import cv2
    except ImportError:
        return None
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        return None
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    W = cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0
    H = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0
    if total <= 0 or W <= 0 or H <= 0:
        cap.release()
        return None
    frames_faces = []
    for i in range(samples):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(total * (i + 0.5) / samples))
        ok, frame = cap.read()
        if ok:
            frames_faces.append(_faces(frame, W, H))
    cap.release()
    n = len(frames_faces)
    if n == 0:
        return None
    best, best_count = None, 0
    for faces in frames_faces:
        for f in faces:
            cx, cy = f[0] + f[2] / 2, f[1] + f[3] / 2
            count = sum(1 for other in frames_faces
                        if any(abs(cx - (o[0] + o[2] / 2)) < 0.05 and abs(cy - (o[1] + o[3] / 2)) < 0.05
                               for o in other))
            if count > best_count:
                best, best_count = f, count
    if not best or best_count < max(3, n * 0.35):
        return None
    fx, fy, fw, fh = best
    if fh > 0.45:
        return None  # камера на весь экран — отдельная вебка не нужна
    reg_w_px = min(fw * W * 2.8, W * 0.6)
    reg_h_px = reg_w_px / cam_aspect
    cx_px = (fx + fw / 2) * W
    cy_px = (fy + fh / 2) * H + reg_h_px * 0.08
    x0 = min(max(0.0, cx_px - reg_w_px / 2), W - reg_w_px)
    y0 = min(max(0.0, cy_px - reg_h_px / 2), H - reg_h_px)
    return tuple(round(float(v), 4) for v in (x0 / W, y0 / H, reg_w_px / W, reg_h_px / H))


def grab_stream_frame(kind: str, target: str, name: str, log=print, at: float = 900.0,
                      another: bool = False) -> str | None:
    """Кадр прямо со стрима — чтобы указать вебку, не нарезая клип. kind: "twitch" / "youtube".
    Если стример в эфире — кадр из эфира, иначе — из последней записи (качается всего 2 секунды)."""
    import cv2
    import subprocess
    from . import twitch
    work = os.path.join(paths.default_work_dir(), "frames")
    os.makedirs(work, exist_ok=True)
    raw = os.path.join(work, "grab_raw.png")
    flags = 0x08000000 if os.name == "nt" else 0
    fmt = {"format": "best[height<=720][vcodec!=none]/best"}

    def from_url(media_url: str, seek: float | None = None) -> bool:
        cmd = ["ffmpeg", "-y", "-v", "error"] + (["-ss", str(seek)] if seek else []) + \
              ["-i", media_url, "-frames:v", "1", raw]
        r = subprocess.run(cmd, capture_output=True, timeout=90, creationflags=flags)
        return r.returncode == 0 and os.path.exists(raw)

    import random

    def has_face(path: str) -> bool:
        img = cv2.imread(path)
        return img is not None and bool(_faces(img, img.shape[1], img.shape[0]))
    ok = False
    live_url = f"https://www.twitch.tv/{target}" if kind == "twitch" else twitch.youtube_live_url(target)
    try:  # 1) стример в эфире — берём кадр из эфира («другой кадр» — сначала пробуем запись)
        info = {} if another else twitch.get_info(live_url, fmt)
        if info.get("is_live") and info.get("url"):
            log("Беру кадр из эфира...")
            ok = from_url(info["url"])
    except Exception:
        pass
    if not ok:  # 2) иначе — 2 секунды из последней записи стрима (ищем кадр, где видно лицо)
        try:
            vods = twitch.list_streams(kind, target, 1)
        except Exception as e:
            log(f"Не нашёл записей стрима: {e}")
            vods = []
        if vods:
            v = vods[0]
            dur = v.get("duration") or at * 2
            t = min(at, max(10.0, dur / 3))
            tries = [random.uniform(0.1, 0.9) * dur for _ in range(3)] if another else [t] + \
                [random.uniform(0.1, 0.9) * dur for _ in range(2)]
            log("Беру кадр из последней записи стрима...")
            base = os.path.join(work, "grab_seg")
            for t in tries:
                for f in os.listdir(work):
                    if f.startswith("grab_seg"):
                        try:
                            os.remove(os.path.join(work, f))
                        except OSError:
                            pass
                try:
                    seg = twitch.download_section(v["url"], t, t + 2, base, 720)
                    cap = cv2.VideoCapture(seg)
                    okf, frame = cap.read()
                    cap.release()
                    os.remove(seg)
                    if okf:
                        cv2.imwrite(raw, frame)
                        ok = True
                        if has_face(raw):
                            break  # кадр, где видно лицо, — сразу его
                        log("На этом кадре лица не видно — беру другой момент...")
                except Exception as e:
                    log(f"Не получилось скачать кусок записи: {e}")
        if not ok and another:  # записи нет — хотя бы свежий кадр из эфира
            try:
                info = twitch.get_info(live_url, fmt)
                if info.get("is_live") and info.get("url"):
                    ok = from_url(info["url"])
            except Exception:
                pass
    if not ok:
        return None
    frame = cv2.imread(raw)
    if frame is None:
        return None
    h, w = frame.shape[:2]
    frame = cv2.resize(frame, (960, int(960 * h / w)))
    out = frame_path(name)
    cv2.imwrite(out, frame)
    try:
        os.remove(raw)
    except OSError:
        pass
    return out
