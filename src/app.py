"""
Aplicacion web - Deteccion de Microexpresiones Faciales
Ejecutar: streamlit run src/app.py
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Deque, List
from collections import deque

import cv2
import numpy as np
import pandas as pd
import streamlit as st

from src.config import DEFAULT_LABELS, get_settings
from src.model import load_model, predict_emotion
from src.model_advanced import load_advanced_model, predict_emotion_advanced
from src.preprocessing import FaceDetector, extract_face_roi, sequence_to_motion_features, to_gray

st.set_page_config(
    page_title="MicroExpr - Analisis Facial",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root {
    --bg-main: #0b1224;
    --bg-panel: #111b34;
    --bg-soft: #162548;
    --text-main: #f7fbff;
    --text-soft: #b7c8ea;
    --accent: #ff6b35;
    --accent-2: #00c2a8;
    --line: #28406f;
}

html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(1000px 450px at 78% -10%, #223f73 0%, #0b1224 58%) fixed;
    color: var(--text-main) !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e1a35 0%, #0a1430 100%) !important;
    border-right: 1px solid var(--line);
}

[data-testid="stSidebar"] * {
    color: var(--text-main) !important;
}

.main-wrap {
    border: 1px solid var(--line);
    background: linear-gradient(165deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
    border-radius: 20px;
    padding: 26px;
    margin-bottom: 18px;
    backdrop-filter: blur(6px);
}

.hero {
    border-radius: 18px;
    padding: 28px;
    border: 1px solid #36538a;
    background: linear-gradient(125deg, #1b2f58 0%, #233f73 35%, #bf4a2a 100%);
    box-shadow: 0 16px 40px rgba(0,0,0,0.33);
    margin-bottom: 16px;
}

.hero h1 {
    margin: 0 0 8px 0;
    color: #ffffff !important;
    font-size: 2.15rem;
    font-weight: 900;
    letter-spacing: 0.2px;
}

.hero p {
    margin: 0;
    color: #e9f2ff !important;
    font-size: 1rem;
}

.subcard {
    background: linear-gradient(180deg, #101d3a 0%, #0f1a34 100%);
    border: 1px solid #2f4d84;
    border-radius: 14px;
    padding: 16px;
    margin: 10px 0;
}

.section-title {
    font-weight: 800;
    font-size: 1.1rem;
    color: #ffffff !important;
    margin-bottom: 8px;
}

.pill {
    display: inline-block;
    border-radius: 999px;
    padding: 5px 12px;
    border: 1px solid #3d5f98;
    color: #dceaff;
    font-size: 0.8rem;
    margin-right: 6px;
}

.big-result {
    background: #0f1c38;
    border: 3px solid #ff6b35;
    border-radius: 18px;
    padding: 18px;
    text-align: center;
    margin-top: 12px;
}

.big-result .name {
    font-size: 2.3rem;
    font-weight: 900;
    color: #ff6b35;
}

.big-result .conf {
    font-size: 2.6rem;
    font-weight: 900;
    color: #00c2a8;
}

div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #ff6b35, #e85a2d) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
}

div[data-testid="stButton"] button[kind="secondary"] {
    background: #0f1f3d !important;
    color: #ffffff !important;
    border: 1px solid #35578f !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}

[data-testid="stFileUploader"] {
    background: #0f1c38 !important;
    border: 2px dashed #35578f !important;
    border-radius: 12px !important;
}

[data-testid="stCameraInput"] {
    background: #0f1c38 !important;
    border: 2px dashed #35578f !important;
    border-radius: 12px !important;
}

.stAlert > div {
    color: #ffffff !important;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

EMOTION_ES = {
    "happiness": "Felicidad",
    "sadness": "Tristeza",
    "surprise": "Sorpresa",
    "anger": "Enojo",
    "neutral": "Neutral",
    "disgust": "Disgusto",
    "fear": "Miedo",
    "contempt": "Desprecio",
}

EMOTION_COLORS = {
    "happiness": "#22c55e",
    "sadness": "#60a5fa",
    "surprise": "#f59e0b",
    "anger": "#ef4444",
    "neutral": "#94a3b8",
    "disgust": "#a78bfa",
    "fear": "#f472b6",
    "contempt": "#fb923c",
}


@st.cache_resource(show_spinner="Cargando modelos...")
def load_models(model_path: str, adv_path: str, classes_path: str, adv_classes_path: str):
    model_base, scaler_base, labels_base = None, None, np.array(DEFAULT_LABELS)
    model_adv, scaler_adv, labels_adv = None, None, np.array(DEFAULT_LABELS)

    pkl_base = model_path.replace(".keras", ".pkl")
    pkl_adv = adv_path.replace(".keras", ".pkl")

    if os.path.exists(pkl_base) and os.path.exists(classes_path):
        model_base, scaler_base = load_model(pkl_base)
        labels_base = np.load(classes_path, allow_pickle=True)

    if os.path.exists(pkl_adv) and os.path.exists(adv_classes_path):
        model_adv, scaler_adv = load_advanced_model(pkl_adv)
        labels_adv = np.load(adv_classes_path, allow_pickle=True)

    return model_base, scaler_base, labels_base, model_adv, scaler_adv, labels_adv


@st.cache_resource(show_spinner="Iniciando detector facial...")
def load_detector(detector_type: str) -> FaceDetector:
    return FaceDetector(detector_type)


def simulated_prediction(feature_vector: np.ndarray, labels: np.ndarray):
    seed = int(abs(np.sum(feature_vector)) * 1000) % (2 ** 31)
    rng = np.random.default_rng(seed)
    idx = int(rng.integers(0, len(labels)))
    conf = float(rng.uniform(0.45, 0.82))
    return str(labels[idx]), conf


def classify_sequence(
    gray_list: List[np.ndarray],
    model_base,
    scaler_base,
    labels_base,
    model_adv,
    scaler_adv,
    labels_adv,
    mode: str,
):
    fv = sequence_to_motion_features(gray_list)
    if mode == "Basico":
        if model_base is None:
            return simulated_prediction(fv, labels_base)
        cid, conf, _ = predict_emotion(model_base, scaler_base, fv)
        return str(labels_base[cid]), conf
    if model_adv is None:
        return simulated_prediction(fv, labels_adv)
    cid, conf, _ = predict_emotion_advanced(model_adv, scaler_adv, fv)
    return str(labels_adv[cid]), conf


def annotate_frame(frame: np.ndarray, bbox, emotion: str, confidence: float, threshold: float):
    x, y, w, h = bbox
    color = (0, 200, 80) if confidence >= threshold else (0, 80, 220)
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    nombre = EMOTION_ES.get(emotion, emotion)
    label = f"{nombre}  {confidence * 100:.1f}%"
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.62, 2)
    cv2.rectangle(frame, (x, max(0, y - th - 12)), (x + tw + 8, y), color, -1)
    cv2.putText(frame, label, (x + 4, max(th, y - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2)


def analyze_camera_photo(
    photo_bytes: bytes,
    mode: str,
    settings,
    detector: FaceDetector,
    model_base,
    scaler_base,
    labels_base,
    model_adv,
    scaler_adv,
    labels_adv,
):
    """
    Analiza una foto de camara y retorna un dict con:
      - 'annotated_rgb': np.ndarray RGB con bbox y etiqueta dibujados
      - 'annotated_png': bytes PNG descargable
      - 'emotion': str
      - 'nombre': str traducido al espanol
      - 'confidence': float 0-1
      - 'color': str hex
      - 'bbox': tuple (x,y,w,h) o None
      - 'error': str o None
      - 'face_detected': bool
    """
    arr = np.frombuffer(photo_bytes, np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        return {"error": "No se pudo leer la foto.", "face_detected": False}

    bbox = detector.detect(frame)
    if bbox is None:
        raw_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return {
            "error": None,
            "face_detected": False,
            "annotated_rgb": raw_rgb,
        }

    face_gray = to_gray(extract_face_roi(frame, bbox, output_size=settings.face_size))
    pseudo_seq = [face_gray] * settings.sequence_length

    emotion, confidence = classify_sequence(
        pseudo_seq,
        model_base,
        scaler_base,
        labels_base,
        model_adv,
        scaler_adv,
        labels_adv,
        mode,
    )

    annotate_frame(frame, bbox, emotion, confidence, settings.confidence_threshold)

    annotated_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    ok, buf = cv2.imencode(".png", frame)
    png_bytes = buf.tobytes() if ok else b""

    x, y, w, h = bbox
    return {
        "error": None,
        "face_detected": True,
        "annotated_rgb": annotated_rgb,
        "annotated_png": png_bytes,
        "emotion": emotion,
        "nombre": EMOTION_ES.get(emotion, emotion),
        "confidence": confidence,
        "color": EMOTION_COLORS.get(emotion, "#ff6b35"),
        "bbox": (x, y, w, h),
    }


def process_uploaded_video(
    video_path: str,
    mode: str,
    settings,
    detector: FaceDetector,
    model_base,
    scaler_base,
    labels_base,
    model_adv,
    scaler_adv,
    labels_adv,
):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("No se pudo abrir el video.")
        return []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    preview = st.empty()
    progress = st.empty()
    info = st.empty()

    buffer: Deque[np.ndarray] = deque(maxlen=settings.sequence_length)
    results: List[dict] = []
    frame_idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_idx += 1

        bbox = detector.detect(frame)
        if bbox is not None:
            face = extract_face_roi(frame, bbox, output_size=settings.face_size)
            buffer.append(to_gray(face))

            if len(buffer) == settings.sequence_length:
                emotion, confidence = classify_sequence(
                    list(buffer),
                    model_base,
                    scaler_base,
                    labels_base,
                    model_adv,
                    scaler_adv,
                    labels_adv,
                    mode,
                )
                annotate_frame(frame, bbox, emotion, confidence, settings.confidence_threshold)
                results.append(
                    {
                        "Frame": frame_idx,
                        "Emocion": emotion,
                        "Nombre": EMOTION_ES.get(emotion, emotion),
                        "Confianza (%)": round(confidence * 100, 2),
                    }
                )

        preview.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="Analisis en progreso", width="stretch")
        if total_frames > 0:
            progress.progress(min(frame_idx / total_frames, 1.0), text=f"Frame {frame_idx} de {total_frames}")
        info.caption(f"Procesando: {frame_idx} frames")

    cap.release()
    return results


def render_sidebar(settings, mode):
    st.sidebar.title("MicroExpr")
    st.sidebar.caption("Deteccion de Microexpresiones")
    st.sidebar.markdown("<div class='pill'>Flujo Optico</div><div class='pill'>Scikit-learn</div>", unsafe_allow_html=True)
    st.sidebar.divider()

    st.sidebar.write("Modelo activo")
    mode = st.sidebar.radio(
        "Selecciona el modelo",
        ["Basico", "Avanzado (Ensemble)"],
        index=0 if mode == "Basico" else 1,
    )

    base_pkl = settings.model_path.replace(".keras", ".pkl")
    adv_pkl = settings.advanced_model_path.replace(".keras", ".pkl")

    st.sidebar.divider()
    st.sidebar.write("Estado")
    if os.path.exists(base_pkl):
        st.sidebar.success("Modelo Basico listo")
    else:
        st.sidebar.warning("Modelo Basico no entrenado")

    if os.path.exists(adv_pkl):
        st.sidebar.success("Modelo Avanzado listo")
    else:
        st.sidebar.warning("Modelo Avanzado no entrenado")

    st.sidebar.divider()
    st.sidebar.caption("Tip: para resultados reales entrena primero con videos propios")

    return mode


def render_header():
    st.markdown(
        """
<div class="hero"> 
    <h1>Analizador de Microexpresiones Faciales</h1>
    <p>Camara en vivo o video subido. Resultado visual inmediato y exportable.</p>
</div>
""",
        unsafe_allow_html=True,
    )


def build_burst_video_bytes(frames_bytes: list, fps: int = 8) -> bytes:
    """
    Ensambla fotos JPEG de camara en un archivo AVI con codec XVID.
    Retorna bytes del archivo AVI listo para descarga.
    """
    if not frames_bytes:
        return b""

    decoded = []
    for raw in frames_bytes:
        arr = np.frombuffer(raw, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is not None:
            decoded.append(img)

    if not decoded:
        return b""

    h, w = decoded[0].shape[:2]
    out_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".avi") as tmp:
            out_path = tmp.name

        writer = cv2.VideoWriter(
            out_path,
            cv2.VideoWriter_fourcc(*"XVID"),
            fps,
            (w, h),
        )
        if not writer.isOpened():
            return b""

        for frame in decoded:
            if frame.shape[:2] != (h, w):
                frame = cv2.resize(frame, (w, h))
            writer.write(frame)

        writer.release()
        with open(out_path, "rb") as f:
            return f.read()
    finally:
        if out_path and os.path.exists(out_path):
            os.unlink(out_path)


def render_main_panel(
    mode: str,
    settings,
    detector,
    model_base,
    scaler_base,
    labels_base,
    model_adv,
    scaler_adv,
    labels_adv,
):
    st.markdown("<div class='main-wrap'>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Fuente de entrada</div>", unsafe_allow_html=True)

    source = st.radio(
        "Elige como analizar",
        ["Camara web", "Subir video"],
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown("<div class='subcard'>", unsafe_allow_html=True)

    base_pkl = settings.model_path.replace(".keras", ".pkl")
    adv_pkl = settings.advanced_model_path.replace(".keras", ".pkl")
    simulated = (mode == "Basico" and not os.path.exists(base_pkl)) or (
        mode == "Avanzado (Ensemble)" and not os.path.exists(adv_pkl)
    )
    if simulated:
        st.warning("Modo demo activo: aun no hay modelo entrenado. Puedes probar la interfaz con datos simulados.")

    # --- Estado de sesion para camara ---
    if "camera_on" not in st.session_state:
        st.session_state.camera_on = False
    if "cam_mode" not in st.session_state:
        st.session_state.cam_mode = "Foto unica"
    if "burst_frames" not in st.session_state:
        st.session_state.burst_frames = []
    if "burst_video_bytes" not in st.session_state:
        st.session_state.burst_video_bytes = None
    if "burst_results" not in st.session_state:
        st.session_state.burst_results = None

    if source == "Camara web":
        st.markdown("<div class='section-title'>Control de camara</div>", unsafe_allow_html=True)

        # Botones encender / apagar
        c1, c2, _ = st.columns([1, 1, 3])
        with c1:
            if st.button("Encender camara", type="primary", key="btn_cam_on"):
                st.session_state.camera_on = True
        with c2:
            if st.button("Apagar camara", type="secondary", key="btn_cam_off"):
                st.session_state.camera_on = False
                st.session_state.burst_frames = []
                st.session_state.burst_video_bytes = None
                st.session_state.burst_results = None
                st.rerun()

        if not st.session_state.camera_on:
            st.caption("La camara esta apagada. Presiona **Encender camara** para iniciar.")
        else:
            # ----------------------------------------------------------------
            # FLUJO SIMPLE: camara → foto → resultado visible al instante
            # ----------------------------------------------------------------
            st.caption("Colócate frente a la camara y presiona el botón circular para capturar.")

            photo = st.camera_input(
                "Captura",
                label_visibility="collapsed",
                key="cam_single",
            )

            # El resultado aparece AQUI, justo debajo de la camara
            if photo is not None:
                result = analyze_camera_photo(
                    photo.getvalue(),
                    mode,
                    settings,
                    detector,
                    model_base,
                    scaler_base,
                    labels_base,
                    model_adv,
                    scaler_adv,
                    labels_adv,
                )

                if result.get("error"):
                    st.error(result["error"])

                elif not result["face_detected"]:
                    # Sin rostro: mostrar imagen + aviso
                    st.markdown(
                        """
<div style="background:#1a0a0a;border:2px solid #ef4444;border-radius:12px;
     padding:12px 16px;color:#fca5a5;margin:8px 0;">
  <b>&#x26A0; Rostro no detectado</b><br>
  <span style="font-size:0.87rem;">
  Acercate mas &bull; Mejora la luz frontal &bull; Mira directo a la camara
  </span>
</div>
""",
                        unsafe_allow_html=True,
                    )
                    st.image(
                        result["annotated_rgb"],
                        caption="Foto capturada (sin rostro detectado)",
                        width="stretch",
                    )

                else:
                    # CON ROSTRO: imagen anotada + tarjeta de resultado
                    color = result["color"]
                    nombre = result["nombre"]
                    emotion = result["emotion"]
                    confidence = result["confidence"]
                    x, y, w, h = result["bbox"]
                    img_h, img_w = result["annotated_rgb"].shape[:2]
                    face_pct = (w * h) / (img_w * img_h) * 100

                    base_pkl = settings.model_path.replace(".keras", ".pkl")
                    adv_pkl = settings.advanced_model_path.replace(".keras", ".pkl")
                    is_simulated = (mode == "Basico" and not os.path.exists(base_pkl)) or (
                        mode == "Avanzado (Ensemble)" and not os.path.exists(adv_pkl)
                    )

                    col_img, col_res = st.columns([3, 2])

                    with col_img:
                        # Imagen anotada (con el recuadro y etiqueta ya dibujados)
                        st.image(
                            result["annotated_rgb"],
                            caption="Foto con rostro detectado y emocion etiquetada",
                            width="stretch",
                        )
                        # Descarga de la imagen anotada
                        if result.get("annotated_png"):
                            st.download_button(
                                "Descargar foto con resultado (.png)",
                                data=result["annotated_png"],
                                file_name="resultado_microexpr.png",
                                mime="image/png",
                                type="secondary",
                                key="btn_dl_foto",
                            )

                    with col_res:
                        st.markdown(
                            f"""
<div class="big-result" style="border-color:{color};margin-top:0;">
  <div style="font-size:0.72rem;color:#a8bde8;letter-spacing:1px;">ROSTRO DETECTADO</div>
  <div style="font-size:0.78rem;color:#60a5fa;margin-bottom:10px;">
    {w}&times;{h} px &nbsp;&bull;&nbsp; {face_pct:.1f}% del frame
  </div>
  <div style="font-size:0.72rem;color:#a8bde8;letter-spacing:1px;">EMOCION</div>
  <div class="name" style="color:{color};font-size:2rem;">{nombre.upper()}</div>
  <div style="font-size:0.85rem;color:#d4e3ff;margin-bottom:10px;">{emotion}</div>
  <div style="font-size:0.72rem;color:#a8bde8;letter-spacing:1px;">CONFIANZA</div>
  <div class="conf">{confidence * 100:.1f}%</div>
  <div style="margin-top:12px;font-size:0.75rem;color:{'#ffb347' if is_simulated else '#4ade80'};">
    {'&#x26A0; Modo demo (modelo no entrenado)' if is_simulated else '&#x2713; Modelo real activo'}
  </div>
</div>
""",
                            unsafe_allow_html=True,
                        )

            # ----------------------------------------------------------------
            # MODO RAFAGA: expandible para usuarios avanzados
            # ----------------------------------------------------------------
            st.divider()
            with st.expander("Modo ráfaga — captura secuencia y genera video analizable"):
                n_captured = len(st.session_state.burst_frames)
                min_frames = settings.sequence_length

                st.markdown(
                    f"""
<div style="color:#a8bde8;font-size:0.87rem;line-height:1.7;margin-bottom:8px;">
  Haz clic en <b>Capturar</b> {min_frames}+ veces expresando una emocion
  &rarr; pulsa <b>Ensamblar y analizar</b> &rarr; se genera un video MP4 analizado.
  Puedes descargarlo y tambien subirlo en la opcion <i>Subir video</i>.
</div>
""",
                    unsafe_allow_html=True,
                )

                col_bc, col_bs = st.columns([3, 1])
                with col_bc:
                    photo_burst = st.camera_input(
                        "Captura para rafaga",
                        label_visibility="collapsed",
                        key="cam_burst",
                    )
                with col_bs:
                    st.markdown(
                        f"""
<div style="background:#0f1c38;border:2px solid #ff6b35;border-radius:12px;
     padding:14px 8px;text-align:center;margin-top:4px;">
  <div style="font-size:0.72rem;color:#a8bde8;">FOTOS</div>
  <div style="font-size:2.6rem;font-weight:900;color:#ff6b35;">{n_captured}</div>
  <div style="font-size:0.72rem;color:#a8bde8;">min {min_frames}</div>
</div>
""",
                        unsafe_allow_html=True,
                    )

                if photo_burst is not None:
                    new_bytes = photo_burst.getvalue()
                    if not st.session_state.burst_frames or st.session_state.burst_frames[-1] != new_bytes:
                        st.session_state.burst_frames.append(new_bytes)
                        st.session_state.burst_video_bytes = None
                        st.session_state.burst_results = None
                        st.rerun()

                ba1, ba2 = st.columns([2, 1])
                with ba1:
                    can_analyze = n_captured >= min_frames
                    if st.button(
                        f"Ensamblar y analizar ({n_captured} fotos)",
                        type="primary",
                        disabled=not can_analyze,
                        key="btn_burst_analyze",
                    ):
                        with st.spinner("Ensamblando video..."):
                            vb = build_burst_video_bytes(st.session_state.burst_frames)
                        st.session_state.burst_video_bytes = vb
                        if vb:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                                tmp.write(vb)
                                tp = tmp.name
                            with st.spinner("Analizando..."):
                                st.session_state.burst_results = process_uploaded_video(
                                    tp, mode, settings, detector,
                                    model_base, scaler_base, labels_base,
                                    model_adv, scaler_adv, labels_adv,
                                )
                            os.unlink(tp)
                        else:
                            st.error("No se pudo ensamblar el video.")
                with ba2:
                    if st.button("Limpiar", type="secondary", key="btn_burst_clear"):
                        st.session_state.burst_frames = []
                        st.session_state.burst_video_bytes = None
                        st.session_state.burst_results = None
                        st.rerun()

                if not can_analyze and n_captured > 0:
                    st.caption(f"Faltan {min_frames - n_captured} foto(s) mas.")

                if st.session_state.burst_video_bytes:
                    st.success("Video ensamblado correctamente.")
                    st.download_button(
                        "Descargar video de rafaga (.avi) — abrir con VLC",
                        data=st.session_state.burst_video_bytes,
                        file_name="rafaga_microexpr.avi",
                        mime="video/x-msvideo",
                        type="primary",
                        key="btn_dl_burst_video",
                    )
                    st.caption("Descarga el archivo .avi y abrelo con VLC. Tambien puedes subirlo en la seccion 'Subir video'.")

                if st.session_state.burst_results:
                    results_b = st.session_state.burst_results
                    df_b = pd.DataFrame(results_b)
                    top_e = df_b["Emocion"].value_counts().idxmax()
                    top_c = EMOTION_COLORS.get(top_e, "#ff6b35")
                    top_n = EMOTION_ES.get(top_e, top_e)
                    avg_c = df_b[df_b["Emocion"] == top_e]["Confianza (%)"].mean()
                    st.markdown(
                        f"""
<div class="big-result" style="border-color:{top_c};">
  <div style="font-size:0.75rem;color:#a8bde8;">EMOCION PREDOMINANTE</div>
  <div class="name" style="color:{top_c};">{top_n.upper()}</div>
  <div class="conf">{avg_c:.1f}%</div>
  <div style="font-size:0.75rem;color:#a8bde8;">{len(results_b)} detecciones &bull; {n_captured} fotos</div>
</div>
""",
                        unsafe_allow_html=True,
                    )
                    st.dataframe(df_b, hide_index=True)
                    st.download_button(
                        "Descargar CSV",
                        data=df_b.to_csv(index=False, encoding="utf-8").encode("utf-8"),
                        file_name="rafaga_resultados.csv",
                        mime="text/csv",
                        key="btn_dl_burst_csv",
                    )

    else:
        st.markdown("<div class='section-title'>Analisis por video</div>", unsafe_allow_html=True)
        uploaded = st.file_uploader("Sube un video", type=["mp4", "avi", "mov", "mkv"], label_visibility="collapsed")

        if uploaded is None:
            st.caption("Sube un video para comenzar. Recomendado: rostro frontal e iluminacion estable.")
        else:
            st.video(uploaded)
            if st.button("Analizar video", type="primary", width="stretch"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                    tmp.write(uploaded.getvalue())
                    tmp_path = tmp.name

                results = process_uploaded_video(
                    tmp_path,
                    mode,
                    settings,
                    detector,
                    model_base,
                    scaler_base,
                    labels_base,
                    model_adv,
                    scaler_adv,
                    labels_adv,
                )
                os.unlink(tmp_path)

                if results:
                    st.success(f"Analisis completado: {len(results)} detecciones")
                    df = pd.DataFrame(results)
                    st.dataframe(df.tail(60), hide_index=True, width="stretch")
                    st.download_button(
                        "Descargar CSV",
                        data=df.to_csv(index=False, encoding="utf-8").encode("utf-8"),
                        file_name="resultados_microexpresiones.csv",
                        mime="text/csv",
                        type="primary",
                        width="stretch",
                    )
                else:
                    st.warning("No se detectaron rostros en el video.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def main():
    settings = get_settings()

    model_base, scaler_base, labels_base, model_adv, scaler_adv, labels_adv = load_models(
        settings.model_path,
        settings.advanced_model_path,
        settings.classes_path,
        settings.advanced_classes_path,
    )
    detector = load_detector(settings.face_detector)

    if "mode" not in st.session_state:
        st.session_state.mode = "Basico"

    st.session_state.mode = render_sidebar(settings, st.session_state.mode)
    render_header()

    render_main_panel(
        st.session_state.mode,
        settings,
        detector,
        model_base,
        scaler_base,
        labels_base,
        model_adv,
        scaler_adv,
        labels_adv,
    )


if __name__ == "__main__":
    main()

