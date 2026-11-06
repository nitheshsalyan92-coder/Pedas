# 🚦 Pedas — Urban Pedestrian Safety Risk Prediction

A real-time pedestrian safety analysis system built for hackathon. Detects pedestrians and vehicles in video footage, tracks their motion, and predicts conflict risks using CPA (Closest Point of Approach) analysis.

---

## 👥 Team & Modules

| Member | Role | Branch | Module |
|--------|------|--------|--------|
| Member 1 | Frontend Dashboard | `Frontend` | React + Vite UI |
| Member 2 | Backend API | `Backend` | Flask REST API |
| Member 3 | Detection & Tracking | `detection` | `ai/detection.py`, `ai/tracking.py` |
| Member 4 | Risk Analysis & Conflict Detection | `riskanalysis` | `ai/prediction.py` |

---

## 🏗️ Architecture

```
Video Input
    │
    ▼
ai/tracking.py          ← Member 3: YOLOv8 detection + ByteTrack
    │  (tracking records per frame)
    ▼
ai/prediction.py        ← Member 4: CPA conflict detection + risk scoring
    │  (JSON risk result)
    ▼
Backend Flask API       ← Member 2: REST endpoints
    │  (HTTP JSON response)
    ▼
Frontend Dashboard      ← Member 1: React UI with charts and alerts
```

---

## ⚡ Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/nitheshsalyan92-coder/Pedas.git
cd Pedas
```

### 2. Create virtual environment
```bash
python -m venv .venv
.\.venv\Scripts\activate        # Windows
# source .venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install opencv-python ultralytics lapx
```

### 4. Run risk analysis on a sample video
```python
from ai import analyse_video

result = analyse_video("samples/people_sample.mp4")
print(result)
```

---

## 🤖 AI Module — `ai/`

### Core Functions

```python
from ai import analyse_video, analyse_tracks

# Full pipeline: video → tracking → risk analysis
result = analyse_video("path/to/video.mp4")

# Risk analysis only (from pre-computed tracks)
result = analyse_tracks(tracking_records)
```

### Output Schema

```json
{
  "pedestrians_detected": 39,
  "vehicles_detected": 0,
  "conflicts_detected": 2,
  "risk_level": "HIGH",
  "safety_score": 63,
  "alerts": ["CRITICAL conflict between pedestrian 1 and vehicle 3"],
  "conflicts": [...],
  "conflict_details": [...],
  "summary": {
    "total_records": 1500,
    "duration_seconds": 12.4,
    "critical_conflicts": 1,
    "warning_conflicts": 1,
    "caution_conflicts": 0
  }
}
```

### Risk Levels

| Level | Meaning | Safety Score |
|-------|---------|-------------|
| `LOW` | No significant conflicts | 85–100 |
| `MEDIUM` | Warning-level conflicts | 60–84 |
| `HIGH` | Critical conflicts detected | 0–59 |

---

## 🔌 Backend Integration Guide (Member 2)

> **This section is for Member 2** wiring the Flask API to the AI module.

### Install the AI module dependencies
```bash
pip install opencv-python ultralytics lapx
```

### Flask route example

```python
import os
from flask import Flask, request, jsonify
from ai import analyse_video, analyse_tracks

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    # Option A: Accept a video file upload
    video = request.files.get("video")
    if not video:
        return jsonify({"error": "No video provided"}), 400

    video_path = f"uploads/{video.filename}"
    os.makedirs("uploads", exist_ok=True)
    video.save(video_path)

    result = analyse_video(video_path)
    return jsonify(result)


@app.route("/analyze/tracks", methods=["POST"])
def analyze_tracks_route():
    # Option B: Accept pre-computed tracking JSON
    data = request.get_json()
    tracking_records = data.get("tracks", [])

    result = analyse_tracks(tracking_records)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
```

### Key JSON response fields (match these in frontend)

| Field | Type | Description |
|-------|------|-------------|
| `risk_level` | `"LOW"` / `"MEDIUM"` / `"HIGH"` | Overall risk |
| `safety_score` | `0–100` | Safety score (100 = safest) |
| `pedestrians_detected` | int | Count of pedestrians |
| `vehicles_detected` | int | Count of vehicles |
| `conflicts_detected` | int | Number of conflicts |
| `alerts` | list of strings | Human-readable alerts |
| `conflicts` | list of dicts | Conflict details |
| `summary` | dict | Aggregated stats |

### Testing the route (curl)
```bash
# Upload a video
curl -X POST http://localhost:5000/analyze \
  -F "video=@samples/people_sample.mp4"

# Send pre-computed tracks
curl -X POST http://localhost:5000/analyze/tracks \
  -H "Content-Type: application/json" \
  -d '{"tracks": [{"frame": 1, "track_id": 1, "class": "person", "bbox": [100,200,50,80]}]}'
```

---

## 🖥️ Frontend Integration Guide (Member 1)

The backend returns JSON that maps directly to dashboard components:

| Dashboard Component | JSON Field |
|--------------------|------------|
| Risk badge / color | `risk_level` |
| Safety gauge | `safety_score` |
| People count | `pedestrians_detected` |
| Vehicle count | `vehicles_detected` |
| Conflict count | `conflicts_detected` |
| Alert list | `alerts` |
| Timeline / chart | `summary.duration_seconds`, `summary.critical_conflicts` |

---

## 🧪 Running Tests

```bash
# All 25 tests (requires .venv for cv2/ultralytics)
.\.venv\Scripts\python.exe -m unittest discover

# Risk analysis tests only (no special deps)
python -m unittest ai/test_prediction.py

# Detection/tracking tests (requires .venv)
.\.venv\Scripts\python.exe -m unittest tests/test_prediction.py
```

---

## 📁 Project Structure

```
Pedas/
├── ai/
│   ├── __init__.py          # Package exports
│   ├── prediction.py        # Risk analysis engine (Member 4)
│   ├── detection.py         # YOLOv8 object detection (Member 3)
│   ├── tracking.py          # ByteTrack pipeline (Member 3)
│   ├── requirements.txt     # AI module dependencies
│   ├── README.md            # Detailed AI module docs
│   └── sample_tracks.json   # Test data
├── samples/
│   └── people_sample.mp4    # Sample test video
├── tests/
│   ├── test_detection.py
│   ├── test_prediction.py
│   └── test_tracking.py
├── Pedestrian/              # Frontend (Member 1)
├── .gitignore
└── README.md                # This file
```

---

## 📌 Notes

- `.venv/` is excluded from git — each member must create their own virtual environment
- `yolov8n.pt` model weights are auto-downloaded by `ultralytics` on first run
- Generated output videos (`annotated_*.mp4`) are excluded from git via `.gitignore`
