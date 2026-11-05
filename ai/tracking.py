"""Track pedestrians and vehicles across a road video.

Member 2 calls ``process_video(video_path)``.
Member 4 reads the list this function returns.

Coordinate convention
---------------------
``x`` and ``y`` are the bounding-box centre in video pixels.
Origin is the top-left corner of the frame. ``x`` grows right, ``y`` grows down.

Time
----
``timestamp`` is seconds from the start of the file (frame index / frames per second).

Identity
--------
``object_id`` is the ByteTrack id. Detections ByteTrack has not assigned an id
to are omitted, so every record has a stable id.
"""

from __future__ import annotations

from pathlib import Path

from ai.detection import (
    DEFAULT_CONFIDENCE,
    DEFAULT_MODEL,
    TRACKED_CLASS_IDS,
    load_model,
    object_type_for,
)


def process_video(
    video_path,
    confidence: float = DEFAULT_CONFIDENCE,
    model_name: str = DEFAULT_MODEL,
) -> list[dict]:
    """Detect and track pedestrians and vehicles in ``video_path``.

    Returns one record per tracked object per frame:

    ``object_id``, ``object_type``, ``x``, ``y``, ``timestamp``,
    ``confidence``, and ``bbox`` as ``[x1, y1, x2, y2]`` in pixels.
    """
    path = Path(video_path)
    if not path.is_file():
        raise FileNotFoundError(f"Video not found: {path}")

    fps = _frames_per_second(path)
    model = load_model(model_name)
    frames = model.track(
        source=str(path),
        persist=True,
        tracker="bytetrack.yaml",
        classes=TRACKED_CLASS_IDS,
        conf=confidence,
        stream=True,
        verbose=False,
    )

    records: list[dict] = []
    for frame_index, frame in enumerate(frames):
        boxes = frame.boxes
        if boxes is None or boxes.id is None:
            continue
        timestamp = round(frame_index / fps, 3)
        for box_index, track_id in enumerate(boxes.id.tolist()):
            class_id = int(boxes.cls[box_index].item())
            object_type = object_type_for(class_id)
            if object_type is None:
                continue
            x1, y1, x2, y2 = (round(float(value), 2) for value in boxes.xyxy[box_index].tolist())
            records.append(
                {
                    "object_id": int(track_id),
                    "object_type": object_type,
                    "x": round((x1 + x2) / 2, 2),
                    "y": round((y1 + y2) / 2, 2),
                    "timestamp": timestamp,
                    "confidence": round(float(boxes.conf[box_index].item()), 2),
                    "bbox": [x1, y1, x2, y2],
                }
            )
    return records


def _frames_per_second(path: Path) -> float:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "opencv-python is not installed. From the repo root run: "
            "pip install -r ai/requirements.txt"
        ) from exc

    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise ValueError(f"Could not read video: {path}")
        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0)
    finally:
        capture.release()
    if fps <= 0:
        raise ValueError(f"Video has no frame rate: {path}")
    return fps


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 2:
        print("usage: python -m ai.tracking <video_path>", file=sys.stderr)
        raise SystemExit(2)
    print(json.dumps(process_video(sys.argv[1]), indent=2))
