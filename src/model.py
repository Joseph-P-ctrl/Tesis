"""
Módulo del modelo de clasificación de microexpresiones.
Usa scikit-learn (MLPClassifier) para compatibilidad con Python 3.14+.
"""
from __future__ import annotations

from typing import Tuple

import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import joblib


def build_feature_classifier(
    num_classes: int,
    hidden_layer_sizes: Tuple[int, ...] = (256, 128, 64),
    max_iter: int = 500,
    learning_rate_init: float = 1e-3,
    random_state: int = 42,
) -> MLPClassifier:
    """Construye y devuelve un clasificador MLP (red neuronal) de scikit-learn."""
    model = MLPClassifier(
        hidden_layer_sizes=hidden_layer_sizes,
        activation="relu",
        solver="adam",
        alpha=1e-4,                    # regularización L2
        batch_size="auto",
        learning_rate_init=learning_rate_init,
        max_iter=max_iter,
        shuffle=True,
        random_state=random_state,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=15,
        verbose=False,
    )
    return model


def build_scaler() -> StandardScaler:
    """Devuelve un escalador estándar para normalizar features."""
    return StandardScaler()


def save_model(model: MLPClassifier, scaler: StandardScaler, model_path: str) -> None:
    """Guarda modelo y scaler en un archivo .pkl usando joblib."""
    joblib.dump({"model": model, "scaler": scaler}, model_path)


def load_model(model_path: str) -> Tuple[MLPClassifier, StandardScaler]:
    """Carga modelo y scaler desde archivo .pkl."""
    bundle = joblib.load(model_path)
    return bundle["model"], bundle["scaler"]


def predict_emotion(
    model: MLPClassifier,
    scaler: StandardScaler,
    feature_vector: np.ndarray,
) -> Tuple[int, float, np.ndarray]:
    """
    Predice la emoción dado un vector de características.
    Devuelve (class_id, confidence, probs_array).
    """
    x = scaler.transform(feature_vector.reshape(1, -1))
    probs = model.predict_proba(x)[0]
    class_id = int(np.argmax(probs))
    confidence = float(probs[class_id])
    return class_id, confidence, probs
