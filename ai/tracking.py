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

# Visualization color mapping (BGR format) for annotated video rendering
COLOR_MAP = {
    "pedestrian": (0, 255, 0),    # Bright green
    "car": (255, 140, 0),         # Cyan / Blue
    "motorcycle": (255, 0, 255),  # Magenta
    "bus": (0, 165, 255),         # Orange
    "truck": (0, 0, 255),         # Red
}
DEFAULT_BOX_COLOR = (200, 200, 200)


def process_video(
    video_path,
    confidence: float = DEFAULT_CONFIDENCE,
    model_name: str = DEFAULT_MODEL,
    output_video_path: str | Path | None = None,
) -> list[dict]:
    """Detect and track pedestrians and vehicles in ``video_path``.

    Returns one record per tracked object per frame:

    ``object_id``, ``object_type``, ``x``, ``y``, ``timestamp``,
    ``confidence``, and ``bbox`` as ``[x1, y1, x2, y2]`` in pixels.

    If ``output_video_path`` is provided, an annotated video with bounding
    boxes, center points, track IDs, and labels is saved to that destination.
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

    video_writer = None
    if output_video_path is not None:
        try:
            import cv2
        except ImportError as exc:
            raise RuntimeError(
                "opencv-python is not installed. From the repo root run: "
                "pip install -r ai/requirements.txt"
            ) from exc
        out_p = Path(output_video_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    try:
        for frame_index, frame in enumerate(frames):
            boxes = frame.boxes
            img = frame.orig_img.copy() if output_video_path is not None else None

            if video_writer is None and output_video_path is not None and img is not None:
                h, w = img.shape[:2]
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                video_writer = cv2.VideoWriter(str(out_p), fourcc, fps, (w, h))

            if boxes is None or boxes.id is None:
                if video_writer is not None and img is not None:
                    video_writer.write(img)
                continue

            timestamp = round(frame_index / fps, 3)
            for box_index, track_id in enumerate(boxes.id.tolist()):
                class_id = int(boxes.cls[box_index].item())
                object_type = object_type_for(class_id)
                if object_type is None:
                    continue
                x1, y1, x2, y2 = (round(float(value), 2) for value in boxes.xyxy[box_index].tolist())
                conf = round(float(boxes.conf[box_index].item()), 2)
                cx = round((x1 + x2) / 2, 2)
                cy = round((y1 + y2) / 2, 2)

                records.append(
                    {
                        "object_id": int(track_id),
                        "object_type": object_type,
                        "x": cx,
                        "y": cy,
                        "timestamp": timestamp,
                        "confidence": conf,
                        "bbox": [x1, y1, x2, y2],
                    }
                )

                if img is not None:
                    color = COLOR_MAP.get(object_type, DEFAULT_BOX_COLOR)
                    cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    cv2.circle(img, (int(cx), int(cy)), 3, (0, 0, 255), -1)
                    label = f"{object_type} #{int(track_id)} {conf:.2f}"
                    cv2.putText(
                        img,
                        label,
                        (int(x1), max(16, int(y1) - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        color,
                        1,
                        cv2.LINE_AA,
                    )

            if video_writer is not None and img is not None:
                video_writer.write(img)
    finally:
        if video_writer is not None:
            video_writer.release()

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

    if len(sys.argv) not in (2, 3):
        print("usage: python -m ai.tracking <video_path> [output_video_path]", file=sys.stderr)
        raise SystemExit(2)
    output_video = sys.argv[2] if len(sys.argv) == 3 else None
    print(json.dumps(process_video(sys.argv[1], output_video_path=output_video), indent=2))
