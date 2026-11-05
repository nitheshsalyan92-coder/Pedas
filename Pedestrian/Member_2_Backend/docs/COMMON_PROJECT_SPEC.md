# Urban Pedestrian Safety Risk Prediction and Conflict Detection

## Project goal
Build a web application that accepts a road-traffic video, detects and tracks pedestrians and vehicles, analyses possible movement conflicts, and displays a Low / Medium / High risk result with alerts.

Important: The system identifies **potential conflicts**, not guaranteed accidents. Do not claim that it can predict accidents with certainty. Do not display fabricated detection results as real AI output.

## Suggested stack
- Frontend: HTML, CSS, JavaScript, Chart.js
- Backend: Python Flask, SQLite
- Computer vision: OpenCV, pretrained YOLO, ByteTrack (if integration is practical)
- Data: JSON between modules

## Shared project structure
```text
Pedestrian-Safety/
  frontend/
  backend/
  ai/
  uploads/
  processed/
  requirements.txt
  README.md
```

## Team integration rules
1. Use one shared GitHub repository.
2. Agree on filenames, API routes, and JSON field names before coding.
3. Commit small changes regularly. Do not overwrite another member's work.
4. Keep each module independent and test it before integration.
5. Integrate early. Do not wait until the final hours.
6. If a feature cannot be completed, clearly label it as a limitation rather than pretending it works.

## Shared data contract (initial proposal)
A tracked object record should contain:
```json
{
  "object_id": 1,
  "object_type": "pedestrian",
  "x": 120,
  "y": 250,
  "timestamp": 2.5,
  "confidence": 0.91
}
```
Coordinates should use a consistent convention (for example, bounding-box centre in video pixels). Agree on this with the AI team.

A risk-analysis result should contain:
```json
{
  "pedestrians_detected": 5,
  "vehicles_detected": 8,
  "conflicts_detected": 2,
  "risk_level": "HIGH",
  "alerts": ["Potential pedestrian-vehicle conflict detected"]
}
```
These are examples of the interface format, not actual results.

## 24-hour build priorities
- First: make the basic end-to-end upload → processing → result flow work.
- Next: improve tracking and risk analysis.
- Then: add charts, reports, styling, and extra features.
- Reserve the final hours for integration, testing, and the presentation.
