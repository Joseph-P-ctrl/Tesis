from collections import deque
from typing import Deque, List, Optional, Tuple

import cv2
import numpy as np

# MediaPipe 0.10+ eliminó mp.solutions; se usa como opcional para compatibilidad.
try:
    import mediapipe as mp
    _MP_SOLUTIONS_OK = hasattr(mp, "solutions")
except ImportError:
    mp = None  # type: ignore
    _MP_SOLUTIONS_OK = False


BoundingBox = Tuple[int, int, int, int]


class FaceDetector:
    """Detector de rostros. Usa Haar (OpenCV) por defecto; MediaPipe como opción legacy."""

    def __init__(self, detector_type: str = "haar") -> None:
        self.detector_type = detector_type
        self.mp_detector = None
        self.haar_detector = None

        if detector_type == "mediapipe" and _MP_SOLUTIONS_OK:
            self.mp_detector = mp.solutions.face_detection.FaceDetection(  # type: ignore[union-attr]
                model_selection=0,
                min_detection_confidence=0.5,
            )
            self.detector_type = "mediapipe"
        else:
            # Fallback a Haar (siempre disponible con OpenCV)
            if detector_type == "mediapipe" and not _MP_SOLUTIONS_OK:
                import warnings
                warnings.warn(
                    "MediaPipe mp.solutions no está disponible en esta versión. "
                    "Usando detector Haar de OpenCV.",
                    RuntimeWarning,
                )
            self.detector_type = "haar"
            self.haar_detector = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )

    def detect(self, frame: np.ndarray) -> Optional[BoundingBox]:
        if self.detector_type == "mediapipe" and self.mp_detector is not None:
            return self._detect_with_mediapipe(frame)
        return self._detect_with_haar(frame)

    def _detect_with_mediapipe(self, frame: np.ndarray) -> Optional[BoundingBox]:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.mp_detector.process(rgb)
        if not result.detections:
            return None

        h, w = frame.shape[:2]
        bbox = result.detections[0].location_data.relative_bounding_box
        x = max(0, int(bbox.xmin * w))
        y = max(0, int(bbox.ymin * h))
        bw = max(1, int(bbox.width * w))
        bh = max(1, int(bbox.height * h))
        return (x, y, bw, bh)

    def _detect_with_haar(self, frame: np.ndarray) -> Optional[BoundingBox]:
        if self.haar_detector is None:
            return None
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.haar_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        if len(faces) == 0:
            return None
        x, y, bw, bh = faces[0]
        return (int(x), int(y), int(bw), int(bh))


def open_video_source(source: str | int) -> cv2.VideoCapture:
    if isinstance(source, str) and source.isdigit():
        source = int(source)
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open source: {source}")
    return cap


def extract_face_roi(frame: np.ndarray, bbox: BoundingBox, output_size: int = 128) -> np.ndarray:
    x, y, w, h = bbox
    pad_x = int(0.15 * w)
    pad_y = int(0.15 * h)

    x1 = max(0, x - pad_x)
    y1 = max(0, y - pad_y)
    x2 = min(frame.shape[1], x + w + pad_x)
    y2 = min(frame.shape[0], y + h + pad_y)

    face = frame[y1:y2, x1:x2]
    if face.size == 0:
        face = np.zeros((output_size, output_size, 3), dtype=np.uint8)
    face = cv2.resize(face, (output_size, output_size))
    return face


def to_gray(face_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)


def init_sequence_buffer(maxlen: int) -> Deque[np.ndarray]:
    return deque(maxlen=maxlen)


def append_frame(buffer: Deque[np.ndarray], frame_gray: np.ndarray) -> None:
    buffer.append(frame_gray)


def compute_dense_optical_flow(prev_gray: np.ndarray, curr_gray: np.ndarray) -> np.ndarray:
    flow = cv2.calcOpticalFlowFarneback(
        prev_gray,
        curr_gray,
        None,
        pyr_scale=0.5,
        levels=3,
        winsize=15,
        iterations=3,
        poly_n=5,
        poly_sigma=1.2,
        flags=0,
    )
    return flow


def flow_to_feature_vector(flow: np.ndarray) -> np.ndarray:
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    features = np.array(
        [
            float(np.mean(mag)),
            float(np.std(mag)),
            float(np.max(mag)),
            float(np.percentile(mag, 25)),
            float(np.percentile(mag, 75)),
            float(np.mean(ang)),
            float(np.std(ang)),
            float(np.mean(np.abs(flow[..., 0] - flow[..., 1]))),
        ],
        dtype=np.float32,
    )
    return features


def sequence_to_motion_features(gray_sequence: List[np.ndarray]) -> np.ndarray:
    if len(gray_sequence) < 2:
        return np.zeros(8, dtype=np.float32)

    frame_features = []
    for i in range(1, len(gray_sequence)):
        flow = compute_dense_optical_flow(gray_sequence[i - 1], gray_sequence[i])
        frame_features.append(flow_to_feature_vector(flow))

    stacked = np.vstack(frame_features)
    return np.mean(stacked, axis=0)


def frame_diff_score(prev_gray: np.ndarray, curr_gray: np.ndarray) -> float:
    diff = cv2.absdiff(prev_gray, curr_gray)
    return float(np.mean(diff))
