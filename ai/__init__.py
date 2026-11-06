"""AI module for pedestrian safety: object detection, tracking, and risk analysis."""

from ai.prediction import analyse_track_file, analyse_tracks, analyse_video


def process_video(*args, **kwargs):
    """Detect and track pedestrians and vehicles in video_path."""
    from ai.tracking import process_video as _process_video

    return _process_video(*args, **kwargs)


__all__ = ["process_video", "analyse_tracks", "analyse_video", "analyse_track_file"]
