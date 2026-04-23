"""
Entrenamiento avanzado: Ensemble (MLP + GBT + RF) con K-Fold + ROC Curves.
No requiere TensorFlow â€” compatible con Python 3.14+.

Uso:
    python -m src.train_advanced --dataset data/dataset --kfold 5
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import List, Tuple

import cv2
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import joblib
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import LabelEncoder, label_binarize

from src.config import get_settings
from src.model_advanced import (
    build_advanced_classifier,
    build_scaler,
    predict_emotion_advanced,
    save_advanced_model,
)
from src.preprocessing import FaceDetector, extract_face_roi, sequence_to_motion_features, to_gray
from src.train import extract_feature_windows, find_videos_by_label, save_metrics


def save_roc_curves(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    class_names: List[str],
    output_path: str,
) -> float:
    """Genera curvas ROC one-vs-rest y guarda la imagen. Devuelve AUC macro."""
    y_bin = label_binarize(y_true, classes=np.arange(len(class_names)))
    plt.figure(figsize=(9, 7))
    colors = plt.cm.get_cmap("tab10", len(class_names))

    auc_scores = []
    for idx, name in enumerate(class_names):
        fpr, tpr, _ = roc_curve(y_bin[:, idx], y_prob[:, idx])
        auc_i = roc_auc_score(y_bin[:, idx], y_prob[:, idx])
        auc_scores.append(auc_i)
        plt.plot(fpr, tpr, color=colors(idx), lw=2, label=f"{name} (AUC={auc_i:.3f})")

    plt.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random")
    plt.xlabel("Tasa de Falsos Positivos")
    plt.ylabel("Tasa de Verdaderos Positivos")
    plt.title("Curvas ROC â€” One-vs-Rest (Modelo Avanzado)")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    return float(np.mean(auc_scores))


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrenamiento avanzado Ensemble + K-Fold")
    parser.add_argument("--dataset", type=str, default=None)
    parser.add_argument("--window_step", type=int, default=4)
    parser.add_argument("--kfold", type=int, default=None)
    args = parser.parse_args()

    settings = get_settings()
    dataset_dir = args.dataset or settings.dataset_dir
    k_folds = args.kfold or settings.k_folds

    samples = find_videos_by_label(dataset_dir)
    if not samples:
        raise RuntimeError("No se encontraron videos. Estructura: data/dataset/<emocion>/*.mp4")

    detector = FaceDetector(settings.face_detector)
    X_list: List[np.ndarray] = []
    y_list: List[str] = []

    print(f"  {len(samples)} videos encontrados. Extrayendo features...")
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
        raise RuntimeError("No se extrajeron features.")

    X = np.vstack(X_list).astype(np.float32)
    y = np.array(y_list)
    print(f"  Dataset: {X.shape[0]} muestras â€” clases: {sorted(set(y_list))}")

    label_encoder = LabelEncoder()
    y_enc = label_encoder.fit_transform(y)
    class_names = list(label_encoder.classes_)

    X_train_all, X_test, y_train_all, y_test = train_test_split(
        X, y_enc,
        test_size=settings.test_size,
        random_state=settings.random_state,
        stratify=y_enc,
    )

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ K-Fold Cross Validation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    skf = StratifiedKFold(n_splits=k_folds, shuffle=True, random_state=settings.random_state)
    fold_results: List[dict] = []

    for fold_idx, (train_idx, val_idx) in enumerate(skf.split(X_train_all, y_train_all), start=1):
        print(f"\n  â”€â”€ Fold {fold_idx}/{k_folds} â”€â”€")
        X_tr, X_val = X_train_all[train_idx], X_train_all[val_idx]
        y_tr, y_val = y_train_all[train_idx], y_train_all[val_idx]

        scaler_fold = build_scaler()
        X_tr  = scaler_fold.fit_transform(X_tr)
        X_val = scaler_fold.transform(X_val)

        model_fold = build_advanced_classifier(
            num_classes=len(class_names),
            random_state=settings.random_state,
        )
        model_fold.fit(X_tr, y_tr)
        val_pred = model_fold.predict(X_val)

        fold_results.append({
            "fold": fold_idx,
            "accuracy":  float(accuracy_score(y_val, val_pred)),
            "precision": float(precision_score(y_val, val_pred, average="weighted", zero_division=0)),
            "recall":    float(recall_score(y_val, val_pred, average="weighted", zero_division=0)),
            "f1":        float(f1_score(y_val, val_pred, average="weighted", zero_division=0)),
        })
        print(f"  acc={fold_results[-1]['accuracy']:.4f}  f1={fold_results[-1]['f1']:.4f}")

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Modelo final (todo el train) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\n  Entrenando modelo final sobre todo el conjunto de entrenamiento...")
    scaler_final = build_scaler()
    X_train_scaled = scaler_final.fit_transform(X_train_all)
    X_test_scaled  = scaler_final.transform(X_test)

    final_model = build_advanced_classifier(
        num_classes=len(class_names),
        random_state=settings.random_state,
    )
    final_model.fit(X_train_scaled, y_train_all)

    y_test_pred = final_model.predict(X_test_scaled)
    y_test_prob = final_model.predict_proba(X_test_scaled)

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Guardar todo â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    advanced_dir = os.path.join(settings.metrics_dir, "advanced")
    os.makedirs(advanced_dir, exist_ok=True)

    adv_model_path = settings.advanced_model_path.replace(".keras", ".pkl")
    save_advanced_model(final_model, scaler_final, adv_model_path)
    np.save(settings.advanced_classes_path, label_encoder.classes_)
    joblib.dump(label_encoder, "models/label_encoder_advanced.pkl")

    # MÃ©tricas holdout
    save_metrics(
        y_true=y_test,
        y_pred=y_test_pred,
        class_names=class_names,
        metrics_dir=advanced_dir,
        prefix="advanced_",
    )

    # ROC Curves
    roc_auc = save_roc_curves(
        y_true=y_test,
        y_prob=y_test_prob,
        class_names=class_names,
        output_path=os.path.join(advanced_dir, "roc_curves_ovr.png"),
    )

    # Resumen CV
    def _mean_std(key: str) -> Tuple[float, float]:
        vals = np.array([r[key] for r in fold_results])
        return float(np.mean(vals)), float(np.std(vals))

    cv_summary = {k: {"mean": _mean_std(k)[0], "std": _mean_std(k)[1]}
                  for k in ("accuracy", "precision", "recall", "f1")}

    holdout = {
        "accuracy":       float(accuracy_score(y_test, y_test_pred)),
        "precision":      float(precision_score(y_test, y_test_pred, average="weighted", zero_division=0)),
        "recall":         float(recall_score(y_test, y_test_pred, average="weighted", zero_division=0)),
        "f1":             float(f1_score(y_test, y_test_pred, average="weighted", zero_division=0)),
        "roc_auc_macro":  roc_auc,
    }

    report = {
        "k_folds": k_folds,
        "classes": class_names,
        "fold_results": fold_results,
        "cv_summary": cv_summary,
        "holdout_metrics": holdout,
    }
    report_path = os.path.join(advanced_dir, "advanced_metrics_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # GrÃ¡fico comparaciÃ³n por fold
    fold_accs = [r["accuracy"] for r in fold_results]
    fold_f1s  = [r["f1"] for r in fold_results]
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(1, k_folds + 1)
    ax.bar(x - 0.2, fold_accs, width=0.4, label="Accuracy", color="steelblue")
    ax.bar(x + 0.2, fold_f1s,  width=0.4, label="F1-score",  color="coral")
    ax.set_xlabel("Fold")
    ax.set_ylabel("Score")
    ax.set_title(f"Resultados K-Fold (k={k_folds})")
    ax.set_xticks(x)
    ax.set_ylim(0, 1)
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(advanced_dir, "kfold_results.png"), dpi=200)
    plt.close()

    print(f"\n  Modelo avanzado guardado: {adv_model_path}")
    print(f"  Reporte: {report_path}")
    print(f"  ROC AUC macro: {roc_auc:.4f}")


if __name__ == "__main__":
    main()

