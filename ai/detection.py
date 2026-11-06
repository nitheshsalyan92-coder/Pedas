"""Road-user detection with a pretrained YOLO model.

Do not train a model for this project. ``ultralytics`` downloads a small
pretrained checkpoint (``yolov8n.pt``) on first use.

Confidence threshold
--------------------
``DEFAULT_CONFIDENCE`` is 0.40. Detections below this score are dropped
before tracking. Raise it when the clip is noisy. Lower it only when
pedestrians or vehicles are being missed.
"""

from __future__ import annotations

DEFAULT_CONFIDENCE = 0.40
DEFAULT_MODEL = "yolov8n.pt"

# COCO class ids from the pretrained YOLOv8 weights.
# "person" is reported as "pedestrian" so Member 4 can split road users
# with object_type alone.
OBJECT_TYPES = {
    0: "pedestrian",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

TRACKED_CLASS_IDS = list(OBJECT_TYPES)


def load_model(model_name: str = DEFAULT_MODEL):
    """Load a pretrained YOLO checkpoint. Raises if ultralytics is missing."""
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise RuntimeError(
            "ultralytics is not installed. From the repo root run: "
            "pip install -r ai/requirements.txt"
        ) from exc
    return YOLO(model_name)


def object_type_for(class_id: int) -> str | None:
    """Map a COCO class id to the shared object_type name."""
    return OBJECT_TYPES.get(int(class_id))
