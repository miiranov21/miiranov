"""Автопоиск вебки стримера на кадре (OpenCV, необязательно)."""
from __future__ import annotations


def detect_facecam(video: str, samples: int = 14, cam_aspect: float = 1080 / 672):
    """Возвращает (x, y, w, h) области вебки в долях кадра или None.
    Ищем лицо, которое стоит на одном месте в большинстве кадров (оверлей вебки),
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
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    frames_faces = []
    for i in range(samples):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(total * (i + 0.5) / samples))
        ok, frame = cap.read()
        if not ok:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6,
                                         minSize=(int(H * 0.05), int(H * 0.05)))
        frames_faces.append([(x / W, y / H, w / W, h / H) for (x, y, w, h) in faces])
    cap.release()
    n = len(frames_faces)
    if n == 0:
        return None
    # самое «устойчивое» лицо: встречается примерно в одном месте в большинстве кадров
    best, best_count = None, 0
    for faces in frames_faces:
        for f in faces:
            cx, cy = f[0] + f[2] / 2, f[1] + f[3] / 2
            count = 0
            for other in frames_faces:
                if any(abs(cx - (o[0] + o[2] / 2)) < 0.04 and abs(cy - (o[1] + o[3] / 2)) < 0.04 for o in other):
                    count += 1
            if count > best_count:
                best, best_count = f, count
    if not best or best_count < max(3, n * 0.5):
        return None
    fx, fy, fw, fh = best
    if fh > 0.45:
        return None  # камера на весь экран — отдельная вебка не нужна
    # область вебки: лицо + плечи, в пропорции верхней части шортса
    reg_w_px = min(fw * W * 2.6, W * 0.6)
    reg_h_px = reg_w_px / cam_aspect
    cx_px = (fx + fw / 2) * W
    cy_px = (fy + fh / 2) * H + reg_h_px * 0.08
    x0 = min(max(0.0, cx_px - reg_w_px / 2), W - reg_w_px)
    y0 = min(max(0.0, cy_px - reg_h_px / 2), H - reg_h_px)
    return (round(x0 / W, 4), round(y0 / H, 4), round(reg_w_px / W, 4), round(reg_h_px / H, 4))
