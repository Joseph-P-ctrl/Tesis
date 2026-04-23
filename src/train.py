"""
Script de entrenamiento del modelo base (MLP / scikit-learn).
Extrae features de optical flow de videos etiquetados y entrena el clasificador.
No requiere TensorFlow — compatible con Python 3.14+.

Uso:
    python -m src.train --dataset data/dataset
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import List, Tuple

import cv2
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from src.config import get_settings
from src.model import (
    build_feature_classifier,
    build_scaler,
    predict_emotion,
    save_model,
)
from src.preprocessing import FaceDetector, extract_face_roi, sequence_to_motion_features, to_gray
import joblib


VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}


def find_videos_by_label(dataset_dir: str) -> List[Tuple[str, str]]:
    """Recorre dataset_dir/<label>/<video> y devuelve lista de (path, label)."""
    samples: List[Tuple[str, str]] = []
    root = Path(dataset_dir)
    if not root.exists():
        return samples
    for label_dir in root.iterdir():
        if not label_dir.is_dir():
            continue
        for file_path in label_dir.rglob("*"):
            if file_path.suffix.lower() in VIDEO_EXTS:
                samples.append((str(file_path), label_dir.name))
    return samples


def extract_feature_windows(
    video_path: str,
    detector: FaceDetector,
    sequence_length: int,
    face_size: int,
    window_step: int,
) -> List[np.ndarray]:
    """Extrae vectores de características de movimiento usando ventanas deslizantes."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    gray_faces: List[np.ndarray] = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        bbox = detector.detect(frame)
        if bbox is None:
            continue
        face = extract_face_roi(frame, bbox, output_size=face_size)
        gray_faces.append(to_gray(face))
    cap.release()

    if len(gray_faces) < sequence_length:
        return []

    vectors: List[np.ndarray] = []
    for start in range(0, len(gray_faces) - sequence_length + 1, window_step):
        window = gray_faces[start : start + sequence_length]
        vectors.append(sequence_to_motion_features(window))
    return vectors


def save_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: List[str],
    metrics_dir: str,
    prefix: str = "",
) -> None:
    """Guarda accuracy, precision, recall, F1, confusion matrix y reporte."""
    os.makedirs(metrics_dir, exist_ok=True)

    acc  = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    rec  = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    f1   = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    text = (
        f"accuracy : {acc:.4f}\n"
        f"precision: {prec:.4f}\n"
        f"recall   : {rec:.4f}\n"
        f"f1_score : {f1:.4f}\n\n"
        "Classification report:\n"
        + classification_report(y_true, y_pred, target_names=class_names, zero_division=0)
    )
    score_file = os.path.join(metrics_dir, f"{prefix}scores.txt")
    with open(score_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=class_names, yticklabels=class_names)
    plt.xlabel("Predicho")
    plt.ylabel("Real")
    plt.title(f"Matriz de Confusión{' (' + prefix.strip('_') + ')' if prefix else ''}")
    plt.tight_layout()
    plt.savefig(os.path.join(metrics_dir, f"{prefix}confusion_matrix.png"), dpi=200)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrenamiento del modelo base MLP")
    parser.add_argument("--dataset", type=str, default=None)
    parser.add_argument("--window_step", type=int, default=4)
    args = parser.parse_args()

    settings = get_settings()
    dataset_dir = args.dataset or settings.dataset_dir

    samples = find_videos_by_label(dataset_dir)
    if not samples:
        raise RuntimeError(
            "No se encontraron videos. Estructura esperada: data/dataset/<emocion>/*.mp4"
        )

    detector = FaceDetector(settings.face_detector)
    X_list: List[np.ndarray] = []
    y_list: List[str] = []

    print(f"  {len(samples)} videos encontrados. Extrayendo features de optical flow...")
    for video_path, label in samples:
        vectors = extract_feature_windows(
            video_path=video_path,
            detector=detector,
            sequence_length=settings.sequence_length,
            face_size=settings.face_size,
            window_step=args.window_step,
        )
        if not vectors:
            print(f"  [SKIP] {video_path} — sin rostro detectado o video muy corto")
            continue
        X_list.extend(vectors)
        y_list.extend([label] * len(vectors))

    if not X_list:
        raise RuntimeError("No se extrajeron features. Revisa calidad del video y detección facial.")

    X = np.vstack(X_list).astype(np.float32)
    y = np.array(y_list)
    print(f"  Dataset: {X.shape[0]} muestras — clases: {sorted(set(y_list))}")

    label_encoder = LabelEncoder()
    y_enc = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc,
        test_size=settings.test_size,
        random_state=settings.random_state,
        stratify=y_enc,
    )

    # Normalización: ajusta solo sobre entrenamiento
    scaler = build_scaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = build_feature_classifier(
        num_classes=len(label_encoder.classes_),
        max_iter=settings.epochs * 10,
        learning_rate_init=settings.learning_rate,
        random_state=settings.random_state,
    )

    print("  Entrenando MLP...")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    # Guardar modelo + scaler + clases
    model_path = settings.model_path.replace(".keras", ".pkl")
    save_model(model, scaler, model_path)
    np.save(settings.classes_path, label_encoder.classes_)
    joblib.dump(label_encoder, "models/label_encoder.pkl")

    # Guardar curva de pérdida
    if hasattr(model, "loss_curve_"):
        plt.figure(figsize=(8, 4))
        plt.plot(model.loss_curve_, label="train loss")
        plt.xlabel("Iteración")
        plt.ylabel("Loss")
        plt.title("Curva de pérdida - MLP")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(settings.metrics_dir, "training_loss.png"), dpi=200)
        plt.close()

    save_metrics(
        y_true=y_test,
        y_pred=y_pred,
        class_names=list(label_encoder.classes_),
        metrics_dir=settings.metrics_dir,
    )

    print(f"\n  Modelo guardado en: {model_path}")
    print(f"  Clases: {settings.classes_path}")
    print(f"  Métricas en: {settings.metrics_dir}")


if __name__ == "__main__":
    main()



VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}


def find_videos_by_label(dataset_dir: str) -> List[Tuple[str, str]]:
    samples: List[Tuple[str, str]] = []
    root = Path(dataset_dir)
    if not root.exists():
        return samples

    for label_dir in root.iterdir():
        if not label_dir.is_dir():
            continue
        label = label_dir.name
        for file_path in label_dir.rglob("*"):
            if file_path.suffix.lower() in VIDEO_EXTS:
                samples.append((str(file_path), label))
    return samples


def extract_feature_windows(
    video_path: str,
    detector: FaceDetector,
    sequence_length: int,
    face_size: int,
    window_step: int,
) -> List[np.ndarray]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    gray_faces: List[np.ndarray] = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        bbox = detector.detect(frame)
        if bbox is None:
            continue

        face = extract_face_roi(frame, bbox, output_size=face_size)
        gray_faces.append(to_gray(face))

    cap.release()

    if len(gray_faces) < sequence_length:
        return []

    vectors: List[np.ndarray] = []
    for start in range(0, len(gray_faces) - sequence_length + 1, window_step):
        window = gray_faces[start : start + sequence_length]
        vectors.append(sequence_to_motion_features(window))
    return vectors


def save_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: List[str],
    metrics_dir: str,
) -> None:
    os.makedirs(metrics_dir, exist_ok=True)

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    metrics_text = (
        f"accuracy: {acc:.4f}\n"
        f"precision: {prec:.4f}\n"
        f"recall: {rec:.4f}\n"
        f"f1_score: {f1:.4f}\n"
    )
    with open(os.path.join(metrics_dir, "scores.txt"), "w", encoding="utf-8") as f:
        f.write(metrics_text)
        f.write("\nClassification report:\n")
        f.write(classification_report(y_true, y_pred, target_names=class_names, zero_division=0))

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(os.path.join(metrics_dir, "confusion_matrix.png"), dpi=200)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Train microexpression classifier")
    parser.add_argument("--dataset", type=str, default=None, help="Path to dataset root")
    parser.add_argument("--window_step", type=int, default=4, help="Sliding window step")
    args = parser.parse_args()

    settings = get_settings()
    dataset_dir = args.dataset or settings.dataset_dir

    samples = find_videos_by_label(dataset_dir)
    if not samples:
        raise RuntimeError(
            "No videos found. Use dataset layout: data/dataset/<label_name>/*.mp4"
        )

    detector = FaceDetector(settings.face_detector)
    X_list: List[np.ndarray] = []
    y_list: List[str] = []

    print(f"Found {len(samples)} videos. Extracting motion features...")
    for video_path, label in samples:
        vectors = extract_feature_windows(
            video_path=video_path,
            detector=detector,
            sequence_length=settings.sequence_length,
            face_size=settings.face_size,
            window_step=args.window_step,
        )
        if not vectors:
            continue
        X_list.extend(vectors)
        y_list.extend([label] * len(vectors))

    if not X_list:
        raise RuntimeError("No feature vectors extracted. Check face detection quality.")

    X = np.vstack(X_list).astype(np.float32)
    y = np.array(y_list)

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=settings.test_size,
        random_state=settings.random_state,
        stratify=y_encoded,
    )

    # Standardization often stabilizes training for low-dimensional motion features.
    mean = np.mean(X_train, axis=0)
    std = np.std(X_train, axis=0) + 1e-8
    X_train = (X_train - mean) / std
    X_test = (X_test - mean) / std

    model = build_feature_classifier(
        input_dim=X_train.shape[1],
        num_classes=len(label_encoder.classes_),
        learning_rate=settings.learning_rate,
    )

    history = model.fit(
        X_train,
        y_train,
        validation_data=(X_test, y_test),
        epochs=settings.epochs,
        batch_size=settings.batch_size,
        verbose=1,
    )

    probs = model.predict(X_test, verbose=0)
    y_pred = np.argmax(probs, axis=1)

    model.save(settings.model_path)
    np.save(settings.classes_path, label_encoder.classes_)
    np.save("models/scaler_mean.npy", mean)
    np.save("models/scaler_std.npy", std)

    save_metrics(
        y_true=y_test,
        y_pred=y_pred,
        class_names=list(label_encoder.classes_),
        metrics_dir=settings.metrics_dir,
    )

    plt.figure(figsize=(8, 4))
    plt.plot(history.history["accuracy"], label="train_acc")
    plt.plot(history.history["val_accuracy"], label="val_acc")
    plt.title("Training Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(settings.metrics_dir, "training_accuracy.png"), dpi=200)
    plt.close()

    print("Training completed.")
    print(f"Model saved to: {settings.model_path}")
    print(f"Classes saved to: {settings.classes_path}")
    print(f"Metrics saved in: {settings.metrics_dir}")


if __name__ == "__main__":
    main()
