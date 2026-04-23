import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    dataset_dir: str = os.getenv("DATASET_DIR", "data/dataset")
    model_path: str = os.getenv("MODEL_PATH", "models/microexpr_model.keras")
    advanced_model_path: str = os.getenv("ADVANCED_MODEL_PATH", "models/microexpr_cnn_lstm.keras")
    classes_path: str = os.getenv("CLASSES_PATH", "models/classes.npy")
    advanced_classes_path: str = os.getenv("ADVANCED_CLASSES_PATH", "models/classes_advanced.npy")
    metrics_dir: str = os.getenv("METRICS_DIR", "results/metrics")
    logs_dir: str = os.getenv("LOGS_DIR", "results/logs")

    face_detector: str = os.getenv("FACE_DETECTOR", "haar")
    frame_width: int = int(os.getenv("FRAME_WIDTH", "640"))
    frame_height: int = int(os.getenv("FRAME_HEIGHT", "480"))
    sequence_length: int = int(os.getenv("SEQUENCE_LENGTH", "12"))
    face_size: int = int(os.getenv("FACE_SIZE", "128"))
    flow_size: int = int(os.getenv("FLOW_SIZE", "64"))
    motion_method: str = os.getenv("MOTION_METHOD", "optical_flow")

    test_size: float = float(os.getenv("TEST_SIZE", "0.2"))
    random_state: int = int(os.getenv("RANDOM_STATE", "42"))
    epochs: int = int(os.getenv("EPOCHS", "20"))
    advanced_epochs: int = int(os.getenv("ADVANCED_EPOCHS", "25"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "16"))
    learning_rate: float = float(os.getenv("LEARNING_RATE", "0.001"))
    k_folds: int = int(os.getenv("K_FOLDS", "5"))

    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.35"))
    save_output_video: bool = os.getenv("SAVE_OUTPUT_VIDEO", "false").lower() == "true"
    output_video_path: str = os.getenv("OUTPUT_VIDEO_PATH", "results/logs/output_demo.mp4")
    output_csv_path: str = os.getenv("OUTPUT_CSV_PATH", "results/logs/predictions.csv")


DEFAULT_LABELS = ["happiness", "sadness", "surprise", "anger", "neutral"]


def get_settings() -> Settings:
    settings = Settings()
    os.makedirs(settings.metrics_dir, exist_ok=True)
    os.makedirs(settings.logs_dir, exist_ok=True)
    os.makedirs(os.path.dirname(settings.model_path), exist_ok=True)
    os.makedirs(os.path.dirname(settings.advanced_model_path), exist_ok=True)
    return settings
