"""AI module for pedestrian safety: object detection, tracking, and risk analysis."""


def process_video(*args, **kwargs):
    """Detect and track pedestrians and vehicles in video_path."""
    from ai.tracking import process_video as _process_video

    return _process_video(*args, **kwargs)


def analyse_tracks(*args, **kwargs):
    """Analyse object tracks to identify movement conflicts and overall risk."""
    from ai.prediction import analyse_tracks as _analyse_tracks

    return _analyse_tracks(*args, **kwargs)


__all__ = ["process_video", "analyse_tracks"]
