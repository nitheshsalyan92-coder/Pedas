"""Unit tests for the conflict detection and risk analysis module (Member 4)."""

import json
import tempfile
import unittest
from pathlib import Path

from ai.prediction import (
    analyse_track_file,
    analyse_tracks,
    analyse_video,
    _clean_point,
    _classify,
    _motion,
    _pair_conflict,
    _calculate_safety_score,
)


class TestRiskAnalysis(unittest.TestCase):
    def test_empty_and_invalid_inputs(self):
        # Empty inputs should return LOW risk with 0 detected objects
        for invalid in [None, [], {}, {"tracks": []}, "invalid string"]:
            res = analyse_tracks(invalid)
            self.assertEqual(res["risk_level"], "LOW")
            self.assertEqual(res["pedestrians_detected"], 0)
            self.assertEqual(res["vehicles_detected"], 0)
            self.assertEqual(res["conflicts_detected"], 0)
            self.assertEqual(res["safety_score"], 100)
            self.assertTrue(len(res["alerts"]) > 0)

    def test_corrupted_points_filtering(self):
        corrupted_tracks = [
            {"object_id": 1, "object_type": "pedestrian", "x": "bad", "y": 100, "timestamp": 0.0},
            {"object_id": 1, "object_type": "pedestrian", "x": 100, "y": 100, "timestamp": "invalid"},
            {"not_an_object": True},
            None,
            # One valid point
            {"object_id": 1, "object_type": "pedestrian", "x": 100, "y": 100, "timestamp": 0.0},
        ]
        res = analyse_tracks(corrupted_tracks)
        # Only 1 valid point was extracted, which is too short for motion calculation
        self.assertEqual(res["pedestrians_detected"], 1)
        self.assertEqual(res["conflicts_detected"], 0)
        self.assertEqual(res["risk_level"], "LOW")

    def test_object_classification(self):
        self.assertEqual(_classify("pedestrian"), "pedestrian")
        self.assertEqual(_classify("person"), "pedestrian")
        self.assertEqual(_classify("car"), "vehicle")
        self.assertEqual(_classify("bus"), "vehicle")
        self.assertEqual(_classify("truck"), "vehicle")
        self.assertEqual(_classify("motorcycle"), "vehicle")
        self.assertIsNone(_classify("traffic_light"))
        self.assertIsNone(_classify("tree"))

    def test_motion_estimation(self):
        # Fewer than 2 points
        self.assertIsNone(_motion([{"timestamp": 0.0, "x": 0, "y": 0}]))

        # Exact 2 points
        points = [
            {"timestamp": 0.0, "x": 0.0, "y": 0.0},
            {"timestamp": 1.0, "x": 10.0, "y": 20.0},
        ]
        motion = _motion(points)
        self.assertIsNotNone(motion)
        (vx, vy), speed = motion
        self.assertAlmostEqual(vx, 10.0)
        self.assertAlmostEqual(vy, 20.0)

        # Sliding window with multiple points
        multi_points = [
            {"timestamp": 0.0, "x": 0.0, "y": 0.0},
            {"timestamp": 1.0, "x": 10.0, "y": 0.0},
            {"timestamp": 2.0, "x": 20.0, "y": 0.0},
            {"timestamp": 3.0, "x": 30.0, "y": 10.0},
            {"timestamp": 3.5, "x": 35.0, "y": 20.0},
        ]
        # Window of 1.5s from last point (3.5s) includes points at 2.0, 3.0, 3.5
        motion_recent = _motion(multi_points, recent_window_s=1.5)
        self.assertIsNotNone(motion_recent)
        (vx, vy), speed = motion_recent
        # From t=2.0 (x=20, y=0) to t=3.5 (x=35, y=20) -> dt=1.5, dx=15, dy=20
        self.assertAlmostEqual(vx, 10.0)
        self.assertAlmostEqual(vy, 20 / 1.5, places=2)

    def test_high_risk_conflict(self):
        tracks = [
            {"object_id": 1, "object_type": "pedestrian", "x": 100, "y": 200, "timestamp": 0.0},
            {"object_id": 1, "object_type": "pedestrian", "x": 130, "y": 200, "timestamp": 1.0},
            {"object_id": 2, "object_type": "car", "x": 220, "y": 200, "timestamp": 0.0},
            {"object_id": 2, "object_type": "car", "x": 180, "y": 200, "timestamp": 1.0},
        ]
        res = analyse_tracks(tracks)
        self.assertEqual(res["risk_level"], "HIGH")
        self.assertEqual(res["conflicts_detected"], 1)
        self.assertLessEqual(res["safety_score"], 60)
        conflict = res["conflicts"][0]
        self.assertEqual(conflict["pedestrian_id"], 1)
        self.assertEqual(conflict["vehicle_id"], 2)
        self.assertLessEqual(conflict["time_to_conflict_s"], 2.0)
        self.assertLessEqual(conflict["miss_distance_px"], 45.0)

    def test_diverging_path_no_conflict(self):
        # Pedestrian moving left, vehicle moving right (moving away from each other)
        tracks = [
            {"object_id": 1, "object_type": "pedestrian", "x": 100, "y": 100, "timestamp": 0.0},
            {"object_id": 1, "object_type": "pedestrian", "x": 80, "y": 100, "timestamp": 1.0},
            {"object_id": 2, "object_type": "car", "x": 140, "y": 100, "timestamp": 0.0},
            {"object_id": 2, "object_type": "car", "x": 180, "y": 100, "timestamp": 1.0},
        ]
        res = analyse_tracks(tracks)
        self.assertEqual(res["risk_level"], "LOW")
        self.assertEqual(res["conflicts_detected"], 0)
        self.assertEqual(res["safety_score"], 100)

    def test_analyse_track_file(self):
        sample_path = Path(__file__).parent / "example_tracks.json"
        res = analyse_track_file(sample_path)
        self.assertEqual(res["risk_level"], "HIGH")
        self.assertEqual(res["conflicts_detected"], 1)

    def test_dict_wrapper_input(self):
        sample_path = Path(__file__).parent / "example_tracks.json"
        with open(sample_path, encoding="utf-8") as f:
            raw = json.load(f)
        wrapped = {"tracks": raw}
        res = analyse_tracks(wrapped)
        self.assertEqual(res["risk_level"], "HIGH")

    def test_analyse_video_error_handling(self):
        # Should raise RuntimeError until Member 3's tracking branch is merged
        with self.assertRaises(RuntimeError) as ctx:
            analyse_video("test.mp4")
        self.assertIn("ai.tracking", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
