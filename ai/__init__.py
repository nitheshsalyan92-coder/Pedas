"""Pedestrian risk analysis.

Member 3's detection package exports process_video once that branch is merged.
Until then this package exposes the risk functions only.
"""

from ai.prediction import analyse_track_file, analyse_tracks, analyse_video

__all__ = ["analyse_tracks", "analyse_track_file", "analyse_video"]

try:
    from ai.tracking import process_video
except ImportError:
    process_video = None
else:
    __all__.append("process_video")
