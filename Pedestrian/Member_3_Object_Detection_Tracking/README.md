# Member 3 - AI Object Detection and Tracking

## Your responsibility
Process a road video and produce timestamped pedestrian and vehicle tracks.

## Step-by-step tasks
1. Set up OpenCV and a pretrained YOLO model. Do not spend hackathon time training a model from scratch.
2. Read the uploaded video frame by frame.
3. Detect relevant classes such as person, car, bus, truck, and motorcycle where supported by the model.
4. Keep only detections above a chosen confidence threshold and document that threshold.
5. Track objects across frames using ByteTrack or a simpler available tracker if setup becomes a blocker.
6. Assign stable object IDs where possible.
7. For each tracked object, record object type, bounding-box centre (x, y), timestamp, confidence, and bounding box if useful.
8. Expose one function that accepts a video path and returns structured tracking data.
9. Test on a short sample video and report limitations such as occlusion or poor lighting.

## Expected deliverables
- Working detection and tracking module.
- One callable function such as process_video(video_path).
- Structured tracking output matching the shared data contract.
- Setup instructions and a short test result.

## Suggested files
```text
ai/detection.py, ai/tracking.py
```

## Integration handoff
Send Member 4 the exact object record format, coordinate convention, frame rate/timestamp units, and a sample JSON output. Send Member 2 the function name and required dependencies.

## Before you finish
- Run your module and test it.
- Tell the team what files you created or changed.
- Share exact run commands and dependencies.
- Commit and push your work to your assigned Git branch.
