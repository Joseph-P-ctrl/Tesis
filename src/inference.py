"""
Inferencia en tiempo real o sobre video — modelo base MLP (scikit-learn).
No requiere TensorFlow.

Uso:
    python -m src.inference --source 0              # webcam
    python -m src.inference --source video.mp4      # archivo
"""
from __future__ import annotations

import argparse
import os
from collections import deque
from typing import Deque, Optional, Tuple

import cv2
import numpy as np
import joblib

from src.config import DEFAULT_LABELS, get_settings
from src.model import load_model, predict_emotion
from src.preprocessing import (
    FaceDetector,
    append_frame,
    extract_face_roi,
    open_video_source,
    sequence_to_motion_features,
    to_gray,
)
from src.utils import append_prediction_rows, now_str


def load_trained_assets(model_path: str, classes_path: str):
    """Carga modelo sklearn + scaler. Devuelve (None, labels_default) si no existe."""
    # Acepta ruta con .pkl aunque .env tenga .keras
    pkl_path = model_path.replace(".keras", ".pkl")
    if not (os.path.exists(pkl_path) and os.path.exists(classes_path)):
        return None, None, np.array(DEFAULT_LABELS)
    model, scaler = load_model(pkl_path)
    classes = np.load(classes_path, allow_pickle=True)
    return model, scaler, classes


def simulated_prediction(feature_vector: np.ndarray, labels: np.ndarray) -> Tuple[str, float]:
    motion_energy = float(np.mean(feature_vector[:3]))
    if motion_energy < 0.3:
        emotion = "neutral"
        confidence = 0.78
    elif motion_energy < 0.8:
        emotion = "happiness"
        confidence = 0.66
    else:
        emotion = "surprise"
        confidence = 0.71

    if emotion not in labels:
        emotion = labels[0]
    return emotion, confidence


def draw_prediction(frame: np.ndarray, bbox, emotion: str, confidence: float) -> None:
    x, y, w, h = bbox
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 220, 0), 2)
    text = f"{emotion}: {confidence * 100:.1f}%"
    cv2.putText(frame, text, (x, max(20, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 220, 0), 2)


def run_live_inference(source: str | int, save_csv: bool = True) -> None:
    settings = get_settings()
    detector = FaceDetector(settings.face_detector)

    model, scaler, labels = load_trained_assets(settings.model_path, settings.classes_path)

    cap = open_video_source(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.frame_height)

    writer = None
    if settings.save_output_video:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(
            settings.output_video_path,
            fourcc,
            20.0,
            (settings.frame_width, settings.frame_height),
        )

    frame_buffer: Deque[np.ndarray] = deque(maxlen=settings.sequence_length)
    csv_rows = []
    frame_idx = 0
    mode_label = "MLP (sklearn)" if model is not None else "Simulado"

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame_idx += 1
        bbox = detector.detect(frame)

        if bbox is not None:
            face = extract_face_roi(frame, bbox, output_size=settings.face_size)
            gray = to_gray(face)
            append_frame(frame_buffer, gray)

            if len(frame_buffer) >= settings.sequence_length:
                feature_vector = sequence_to_motion_features(list(frame_buffer))

                if model is None:
                    emotion, confidence = simulated_prediction(feature_vector, labels)
                else:
                    class_id, confidence, _ = predict_emotion(model, scaler, feature_vector)
                    emotion = str(labels[class_id])

                if confidence >= settings.confidence_threshold:
                    draw_prediction(frame, bbox, emotion, confidence)
                    csv_rows.append([now_str(), str(frame_idx), emotion, f"{confidence:.4f}"])
                else:
                    draw_prediction(frame, bbox, "baja_confianza", confidence)
        else:
            cv2.putText(
                frame, "Rostro no detectado", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2,
            )

        # Etiqueta de modo en pantalla
        cv2.putText(frame, f"Modo: {mode_label}", (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

        cv2.imshow("Microexpression Inference  [q=salir]", frame)

        if writer is not None:
            resized = cv2.resize(frame, (settings.frame_width, settings.frame_height))
            writer.write(resized)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()

    if save_csv and csv_rows:
        append_prediction_rows(settings.output_csv_path, csv_rows)
        print(f"Predictions saved in {settings.output_csv_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run microexpression inference")
    parser.add_argument("--source", type=str, default="0", help="Video source (0 webcam or video path)")
    args = parser.parse_args()

    source: str | int
    if args.source.isdigit():
        source = int(args.source)
    else:
        source = args.source

    run_live_inference(source)


if __name__ == "__main__":
    main()
