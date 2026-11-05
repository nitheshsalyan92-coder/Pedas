"""Unit tests for the risk analysis and conflict detection module."""

import json
import unittest
from pathlib import Path

from ai.prediction import analyse_tracks


class TestPrediction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_tracks_path = (
            Path(__file__).resolve().parent.parent / "samples" / "people_sample_tracks.json"
        )

    def test_empty_tracks(self):
        """Empty tracks should return a valid low-risk structure."""
        result = analyse_tracks([])
        self.assertEqual(result["pedestrians_detected"], 0)
        self.assertEqual(result["vehicles_detected"], 0)
        self.assertEqual(result["conflicts_detected"], 0)
        self.assertEqual(result["risk_level"], "LOW")
        self.assertIsInstance(result["alerts"], list)
        self.assertGreater(len(result["alerts"]), 0)

    def test_sample_tracks_pedestrians_only(self):
        """Real sample data containing only pedestrians should produce LOW risk."""
        if not self.sample_tracks_path.is_file():
            self.skipTest(f"Sample tracks not found at {self.sample_tracks_path}")

        with open(self.sample_tracks_path, "r", encoding="utf-8") as f:
            tracks = json.load(f)

        result = analyse_tracks(tracks)
        self.assertEqual(result["pedestrians_detected"], 39)
        self.assertEqual(result["vehicles_detected"], 0)
        self.assertEqual(result["conflicts_detected"], 0)
        self.assertEqual(result["risk_level"], "LOW")
        self.assertTrue(any("No vehicles detected" in alert for alert in result["alerts"]))

    def test_vehicles_only(self):
        """Tracks with only vehicles should produce LOW risk and 0 conflicts."""
        tracks = [
            {"object_id": 10, "object_type": "car", "x": 100.0, "y": 200.0, "timestamp": 0.0},
            {"object_id": 10, "object_type": "car", "x": 120.0, "y": 200.0, "timestamp": 0.1},
            {"object_id": 11, "object_type": "truck", "x": 300.0, "y": 400.0, "timestamp": 0.0},
        ]
        result = analyse_tracks(tracks)
        self.assertEqual(result["pedestrians_detected"], 0)
        self.assertEqual(result["vehicles_detected"], 2)
        self.assertEqual(result["conflicts_detected"], 0)
        self.assertEqual(result["risk_level"], "LOW")

    def test_safe_distant_traffic(self):
        """Pedestrian and vehicle far apart should maintain LOW risk."""
        tracks = [
            # Pedestrian on sidewalk
            {"object_id": 1, "object_type": "pedestrian", "x": 50.0, "y": 50.0, "timestamp": 0.0},
            {"object_id": 1, "object_type": "pedestrian", "x": 52.0, "y": 50.0, "timestamp": 0.1},
            {"object_id": 1, "object_type": "pedestrian", "x": 54.0, "y": 50.0, "timestamp": 0.2},
            # Vehicle on far road lane
            {"object_id": 2, "object_type": "car", "x": 450.0, "y": 300.0, "timestamp": 0.0},
            {"object_id": 2, "object_type": "car", "x": 480.0, "y": 300.0, "timestamp": 0.1},
            {"object_id": 2, "object_type": "car", "x": 510.0, "y": 300.0, "timestamp": 0.2},
        ]
        result = analyse_tracks(tracks)
        self.assertEqual(result["pedestrians_detected"], 1)
        self.assertEqual(result["vehicles_detected"], 1)
        self.assertEqual(result["conflicts_detected"], 0)
        self.assertEqual(result["risk_level"], "LOW")

    def test_critical_converging_conflict_high_risk(self):
        """Vehicle heading directly towards pedestrian at close range produces HIGH risk."""
        # Vehicle moving rapidly towards stationary/slow pedestrian
        tracks = []
        for i, t in enumerate([0.0, 0.1, 0.2, 0.3]):
            # Pedestrian crossing
            tracks.append(
                {
                    "object_id": 1,
                    "object_type": "pedestrian",
                    "x": 200.0,
                    "y": 200.0,
                    "timestamp": t,
                    "bbox": [190.0, 180.0, 210.0, 220.0],
                }
            )
            # Vehicle closing in from 80px down to 35px
            vx = 280.0 - (i * 15.0)  # 280, 265, 250, 235
            tracks.append(
                {
                    "object_id": 2,
                    "object_type": "car",
                    "x": vx,
                    "y": 200.0,
                    "timestamp": t,
                    "bbox": [vx - 20, 185.0, vx + 20, 215.0],
                }
            )

        result = analyse_tracks(tracks)
        self.assertEqual(result["pedestrians_detected"], 1)
        self.assertEqual(result["vehicles_detected"], 1)
        self.assertGreaterEqual(result["conflicts_detected"], 1)
        self.assertEqual(result["risk_level"], "HIGH")

        conflict = result["conflict_details"][0]
        self.assertEqual(conflict["severity"], "CRITICAL")
        self.assertEqual(conflict["pedestrian_id"], 1)
        self.assertEqual(conflict["vehicle_id"], 2)
        self.assertIsNotNone(conflict["estimated_ttc_sec"])
        self.assertLessEqual(conflict["min_distance_px"], 50.0)

    def test_warning_conflict_medium_risk(self):
        """Approaching encounter within warning threshold yields MEDIUM risk."""
        tracks = []
        for i, t in enumerate([0.0, 0.1, 0.2]):
            tracks.append(
                {
                    "object_id": 5,
                    "object_type": "pedestrian",
                    "x": 100.0,
                    "y": 100.0,
                    "timestamp": t,
                }
            )
            # Vehicle approaching within 100px-110px
            vx = 210.0 - (i * 5.0)
            tracks.append(
                {
                    "object_id": 6,
                    "object_type": "motorcycle",
                    "x": vx,
                    "y": 100.0,
                    "timestamp": t,
                }
            )

        result = analyse_tracks(tracks)
        self.assertEqual(result["pedestrians_detected"], 1)
        self.assertEqual(result["vehicles_detected"], 1)
        self.assertEqual(result["conflicts_detected"], 1)
        self.assertEqual(result["risk_level"], "MEDIUM")
        self.assertEqual(result["conflict_details"][0]["severity"], "WARNING")

    def test_interaction_aggregation(self):
        """Consecutive frames of interaction between the same pair should aggregate to 1 conflict."""
        tracks = []
        # 10 consecutive frames of a close encounter
        for i in range(10):
            t = round(i * 0.05, 2)
            tracks.append(
                {"object_id": 1, "object_type": "pedestrian", "x": 150.0, "y": 150.0, "timestamp": t}
            )
            tracks.append(
                {
                    "object_id": 2,
                    "object_type": "car",
                    "x": 180.0 + i * 2,
                    "y": 150.0,
                    "timestamp": t,
                }
            )

        result = analyse_tracks(tracks)
        # Should be aggregated into exactly 1 conflict event
        self.assertEqual(result["conflicts_detected"], 1)
        conflict = result["conflict_details"][0]
        self.assertEqual(conflict["start_time"], 0.0)
        self.assertEqual(conflict["end_time"], 0.45)

    def test_shared_data_contract_keys(self):
        """Ensure all required keys from COMMON_PROJECT_SPEC are present in output."""
        result = analyse_tracks([])
        required_contract_keys = {
            "pedestrians_detected",
            "vehicles_detected",
            "conflicts_detected",
            "risk_level",
            "alerts",
        }
        self.assertTrue(required_contract_keys.issubset(result.keys()))


if __name__ == "__main__":
    unittest.main()
