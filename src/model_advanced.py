"""
Modelo avanzado de clasificación: Ensemble (VotingClassifier).
Combina MLP, GradientBoosting y RandomForest para mayor robustez.
Sin dependencia de TensorFlow — compatible con Python 3.14+.
"""
from __future__ import annotations

from typing import Tuple

import numpy as np
import joblib
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler


def build_advanced_classifier(
    num_classes: int,
    random_state: int = 42,
) -> VotingClassifier:
    """
    Construye un VotingClassifier (soft voting) que combina:
    - MLPClassifier (red neuronal)
    - GradientBoostingClassifier
    - RandomForestClassifier
    """
    mlp = MLPClassifier(
        hidden_layer_sizes=(256, 128, 64),
        activation="relu",
        max_iter=600,
        learning_rate_init=1e-3,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=15,
        random_state=random_state,
    )

    gbc = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        random_state=random_state,
    )

    rfc = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_split=4,
        random_state=random_state,
        n_jobs=-1,
    )

    ensemble = VotingClassifier(
        estimators=[("mlp", mlp), ("gbc", gbc), ("rfc", rfc)],
        voting="soft",
        weights=[2, 1, 1],           # le damos más peso al MLP
    )
    return ensemble


def build_scaler() -> StandardScaler:
    return StandardScaler()


def save_advanced_model(
    model: VotingClassifier,
    scaler: StandardScaler,
    model_path: str,
) -> None:
    joblib.dump({"model": model, "scaler": scaler}, model_path)


def load_advanced_model(
    model_path: str,
) -> Tuple[VotingClassifier, StandardScaler]:
    bundle = joblib.load(model_path)
    return bundle["model"], bundle["scaler"]


def predict_emotion_advanced(
    model: VotingClassifier,
    scaler: StandardScaler,
    feature_vector: np.ndarray,
) -> Tuple[int, float, np.ndarray]:
    x = scaler.transform(feature_vector.reshape(1, -1))
    probs = model.predict_proba(x)[0]
    class_id = int(np.argmax(probs))
    confidence = float(probs[class_id])
    return class_id, confidence, probs
