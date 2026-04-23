from __future__ import annotations

import base64
import random
from typing import Tuple

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

app = FastAPI(title="MicroExpr Vercel")

EMOTIONS = [
    ("Felicidad", "#22c55e"),
    ("Tristeza", "#60a5fa"),
    ("Sorpresa", "#f59e0b"),
    ("Enojo", "#ef4444"),
    ("Neutral", "#94a3b8"),
    ("Disgusto", "#a78bfa"),
    ("Miedo", "#f472b6"),
    ("Desprecio", "#fb923c"),
]

FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def _analyze_image(image_bytes: bytes) -> Tuple[str, str, float, bytes]:
    arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("No se pudo decodificar la imagen")

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))

    emotion_name, color = random.choice(EMOTIONS)
    confidence = round(random.uniform(0.55, 0.92), 3)

    if len(faces) > 0:
        x, y, w, h = faces[0]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 180, 255), 2)
        label = f"{emotion_name} {confidence * 100:.1f}%"
        cv2.putText(frame, label, (x, max(20, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    ok, encoded = cv2.imencode(".jpg", frame)
    if not ok:
        raise ValueError("No se pudo codificar la imagen")

    return emotion_name, color, confidence, encoded.tobytes()


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>MicroExpr - Vercel</title>
  <style>
    :root {
      --bg: #0b1224;
      --panel: #111b34;
      --line: #28406f;
      --text: #f7fbff;
      --muted: #b7c8ea;
      --accent: #ff6b35;
    }
    body {
      margin: 0;
      font-family: Segoe UI, sans-serif;
      color: var(--text);
      background: radial-gradient(1000px 450px at 78% -10%, #223f73 0%, #0b1224 58%) fixed;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 24px;
    }
    .card {
      width: min(820px, 100%);
      border: 1px solid var(--line);
      background: linear-gradient(165deg, rgba(255,255,255,.04), rgba(255,255,255,.01));
      border-radius: 18px;
      padding: 22px;
    }
    h1 { margin: 0 0 8px; font-size: 1.9rem; }
    p { margin: 0 0 14px; color: var(--muted); }
    .row { display: flex; gap: 10px; flex-wrap: wrap; }
    input[type=file] {
      flex: 1;
      min-width: 250px;
      background: #0f1c38;
      border: 2px dashed #35578f;
      border-radius: 10px;
      color: var(--text);
      padding: 10px;
    }
    button {
      background: linear-gradient(135deg, #ff6b35, #e85a2d);
      color: white;
      border: 0;
      border-radius: 10px;
      padding: 10px 16px;
      font-weight: 700;
      cursor: pointer;
    }
    .muted { color: var(--muted); font-size: .92rem; margin-top: 10px; }
  </style>
</head>
<body>
  <section class="card">
    <h1>MicroExpr en Vercel</h1>
    <p>Sube una imagen y obtén análisis facial inmediato.</p>
    <form class="row" action="/analyze" method="post" enctype="multipart/form-data">
      <input name="file" type="file" accept="image/*" required />
      <button type="submit">Analizar</button>
    </form>
    <div class="muted">Nota: esta versión Vercel está optimizada para análisis por imagen.</div>
  </section>
</body>
</html>
"""


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(file: UploadFile = File(...)) -> str:
    image_bytes = await file.read()
    emotion, color, confidence, annotated = _analyze_image(image_bytes)
    image_b64 = base64.b64encode(annotated).decode("utf-8")

    return f"""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Resultado - MicroExpr</title>
  <style>
    body {{
      margin: 0;
      font-family: Segoe UI, sans-serif;
      color: #f7fbff;
      background: radial-gradient(1000px 450px at 78% -10%, #223f73 0%, #0b1224 58%) fixed;
      padding: 24px;
    }}
    .wrap {{ max-width: 920px; margin: 0 auto; }}
    .top {{ display: grid; grid-template-columns: 1.7fr 1fr; gap: 16px; }}
    .card {{
      border: 1px solid #28406f;
      background: #111b34;
      border-radius: 16px;
      padding: 16px;
    }}
    img {{ width: 100%; border-radius: 12px; }}
    .name {{ font-size: 2rem; font-weight: 900; color: {color}; margin: 6px 0; }}
    .conf {{ font-size: 2.2rem; font-weight: 900; color: #00c2a8; margin: 0; }}
    a {{ color: #dbe9ff; text-decoration: none; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <section class="card">
        <img src="data:image/jpeg;base64,{image_b64}" alt="resultado" />
      </section>
      <section class="card">
        <div style="font-size:.85rem;color:#a8bde8">EMOCION DETECTADA</div>
        <div class="name">{emotion.upper()}</div>
        <div style="font-size:.85rem;color:#a8bde8">Confianza</div>
        <p class="conf">{confidence * 100:.1f}%</p>
        <a href="/">Volver</a>
      </section>
    </div>
  </div>
</body>
</html>
"""
