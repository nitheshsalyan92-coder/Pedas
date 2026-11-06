"""Unit tests for the tracking module."""

import os
import tempfile
import unittest
from pathlib import Path

from ai.tracking import process_video


class TestTracking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Locate sample video relative to the repo directory
        cls.sample_video = Path(__file__).resolve().parent.parent / "samples" / "people_sample.mp4"

    def test_missing_video_raises_filenotfound(self):
        """Non-existent video path must raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            process_video("non_existent_video_12345.mp4")

    def test_process_video_structure(self):
        """Verify tracking output matches the shared data contract."""
        if not self.sample_video.is_file():
            self.skipTest(f"Sample video not found at {self.sample_video}")

        records = process_video(str(self.sample_video))
        self.assertIsInstance(records, list)
        self.assertGreater(len(records), 0)

        required_keys = {"object_id", "object_type", "x", "y", "timestamp", "confidence", "bbox"}
        valid_types = {"pedestrian", "car", "motorcycle", "bus", "truck"}

        for record in records[:50]:  # Inspect first 50 records
            self.assertTrue(required_keys.issubset(record.keys()))
            self.assertIsInstance(record["object_id"], int)
            self.assertIn(record["object_type"], valid_types)
            self.assertIsInstance(record["x"], (int, float))
            self.assertIsInstance(record["y"], (int, float))
            self.assertGreaterEqual(record["timestamp"], 0.0)
            self.assertGreaterEqual(record["confidence"], 0.0)
            self.assertLessEqual(record["confidence"], 1.0)

            bbox = record["bbox"]
            self.assertEqual(len(bbox), 4)
            x1, y1, x2, y2 = bbox
            self.assertLessEqual(x1, x2)
            self.assertLessEqual(y1, y2)

            # Center coordinates check
            expected_cx = round((x1 + x2) / 2, 2)
            expected_cy = round((y1 + y2) / 2, 2)
            self.assertAlmostEqual(record["x"], expected_cx, places=2)
            self.assertAlmostEqual(record["y"], expected_cy, places=2)

    def test_process_video_annotated_output(self):
        """Verify video writer creates an annotated MP4 file when output path is specified."""
        if not self.sample_video.is_file():
            self.skipTest(f"Sample video not found at {self.sample_video}")

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            records = process_video(str(self.sample_video), output_video_path=tmp_path)
            self.assertIsInstance(records, list)
            self.assertTrue(os.path.exists(tmp_path))
            self.assertGreater(os.path.getsize(tmp_path), 0)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
