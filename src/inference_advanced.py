"""
Inferencia avanzada — modelo Ensemble (sklearn VotingClassifier).
No requiere TensorFlow.

Uso:
    python -m src.inference_advanced --source 0
    python -m src.inference_advanced --source video.mp4
"""
from __future__ import annotations

import argparse
import os
from collections import deque
from typing import Deque

import cv2
import numpy as np

from src.config import DEFAULT_LABELS, get_settings
from src.model_advanced import load_advanced_model, predict_emotion_advanced
from src.preprocessing import (
    FaceDetector,
    extract_face_roi,
    open_video_source,
    sequence_to_motion_features,
    to_gray,
)
from src.inference import simulated_prediction, draw_prediction


def run_advanced_inference(source: str | int) -> None:
    settings = get_settings()

    adv_path = settings.advanced_model_path.replace(".keras", ".pkl")
    model, scaler, labels = None, None, np.array(DEFAULT_LABELS)

    if os.path.exists(adv_path) and os.path.exists(settings.advanced_classes_path):
        model, scaler = load_advanced_model(adv_path)
        labels = np.load(settings.advanced_classes_path, allow_pickle=True)
        mode_label = "Ensemble (sklearn)"
    else:
        mode_label = "Simulado (sin modelo)"
        print("  Modelo avanzado no encontrado — usando predicción simulada.")
        print("  Entrena primero con: python -m src.train_advanced --dataset data/dataset")

    detector = FaceDetector(settings.face_detector)
    cap = open_video_source(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.frame_height)

    gray_buffer: Deque[np.ndarray] = deque(maxlen=settings.sequence_length)

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        bbox = detector.detect(frame)
        if bbox is not None:
            face = extract_face_roi(frame, bbox, output_size=settings.face_size)
            gray_buffer.append(to_gray(face))

            if len(gray_buffer) == settings.sequence_length:
                feature_vector = sequence_to_motion_features(list(gray_buffer))

                if model is None:
                    emotion, confidence = simulated_prediction(feature_vector, labels)
                else:
                    class_id, confidence, _ = predict_emotion_advanced(model, scaler, feature_vector)
                    emotion = str(labels[class_id])

                draw_prediction(frame, bbox, emotion, confidence)
        else:
            cv2.putText(frame, "Rostro no detectado", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.putText(frame, f"Modo: {mode_label}", (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)
        cv2.imshow("Microexpression Avanzado  [q=salir]", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def main() -> None:
    parser = argparse.ArgumentParser(description="Advanced inference with CNN-LSTM")
    parser.add_argument("--source", type=str, default="0", help="Video source (0 webcam or video path)")
    args = parser.parse_args()

    source: str | int = int(args.source) if args.source.isdigit() else args.source
    run_advanced_inference(source)


if __name__ == "__main__":
    main()
