"""Unit tests for the detection module."""

import unittest
from ai.detection import (
    DEFAULT_CONFIDENCE,
    DEFAULT_MODEL,
    OBJECT_TYPES,
    TRACKED_CLASS_IDS,
    load_model,
    object_type_for,
)


class TestDetection(unittest.TestCase):
    def test_default_constants(self):
        """Verify default confidence and model settings."""
        self.assertEqual(DEFAULT_CONFIDENCE, 0.40)
        self.assertEqual(DEFAULT_MODEL, "yolov8n.pt")

    def test_coco_mapping(self):
        """Verify COCO class ids map to expected domain terms."""
        self.assertEqual(object_type_for(0), "pedestrian")
        self.assertEqual(object_type_for(2), "car")
        self.assertEqual(object_type_for(3), "motorcycle")
        self.assertEqual(object_type_for(5), "bus")
        self.assertEqual(object_type_for(7), "truck")

    def test_untracked_classes_return_none(self):
        """Classes outside road-user definitions should return None."""
        self.assertIsNone(object_type_for(1))   # bicycle
        self.assertIsNone(object_type_for(15))  # cat
        self.assertIsNone(object_type_for(999)) # non-existent

    def test_tracked_class_ids_match_dict(self):
        """Ensure tracked ids list stays consistent with OBJECT_TYPES dict."""
        self.assertEqual(set(TRACKED_CLASS_IDS), set(OBJECT_TYPES.keys()))

    def test_load_model(self):
        """Verify YOLO model loads properly."""
        model = load_model(DEFAULT_MODEL)
        self.assertIsNotNone(model)


if __name__ == "__main__":
    unittest.main()
