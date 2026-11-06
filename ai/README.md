# AI Conflict Detection & Risk Analysis (Member 4)

This module processes pedestrian and vehicle tracking observations to identify potential spatial-temporal conflicts and evaluate an explainable risk level (`LOW`, `MEDIUM`, or `HIGH`).

> **Safety Notice:** This system flags **potential conflicts** based on geometric convergence and proximity. It does not predict guaranteed accidents.

---

## 1. Architecture & Core Interfaces

### Primary Functions

* `analyse_tracks(tracks: list[dict] | dict) -> dict`
  * Main callable function for Member 2 (Backend) and pipeline integration.
  * Accepts raw tracking observations and returns the risk classification and conflict records.
* `analyse_track_file(file_path: str | Path) -> dict`
  * Helper function to load a JSON file containing tracking observations and evaluate risk.
* `analyse_video(video_path: str | Path, **kwargs) -> dict`
  * Future end-to-end integration wrapper that calls Member 3's `process_video(video_path)` and passes the result into `analyse_tracks()`.

---

## 2. Input Data Contract (from Member 3 Tracking)

The module accepts a list of observation dictionaries (or a dictionary `{"tracks": [...]}`):

```json
[
  {
    "object_id": 1,
    "object_type": "pedestrian",
    "x": 120.5,
    "y": 250.0,
    "timestamp": 2.5,
    "confidence": 0.92,
    "bbox": [100.0, 200.0, 140.0, 300.0]
  }
]
```

* `object_id`: Unique integer assigned by ByteTrack across video frames.
* `object_type`: Road user class (`"pedestrian"`, `"person"`, `"car"`, `"bus"`, `"truck"`, `"motorcycle"`, `"vehicle"`).
* `x`, `y`: Bounding box centre in video pixel coordinates (origin at top-left).
* `timestamp`: Time offset from video start in seconds.
* `confidence` / `bbox`: Optional metadata passed through.

---

## 3. Output Data Contract (to Member 2 Backend & Member 1 Frontend)

```json
{
  "pedestrians_detected": 1,
  "vehicles_detected": 1,
  "conflicts_detected": 1,
  "risk_level": "HIGH",
  "safety_score": 60,
  "alerts": [
    "Pedestrian 1 and vehicle 2 are 50 px apart and their paths converge in 0.7 s (miss 0 px)."
  ],
  "conflicts": [
    {
      "pedestrian_id": 1,
      "vehicle_id": 2,
      "distance_px": 50.0,
      "miss_distance_px": 0.0,
      "closing_speed_px_s": 70.0,
      "time_to_conflict_s": 0.71,
      "risk_level": "HIGH",
      "reason": "Pedestrian 1 and vehicle 2 are 50 px apart and their paths converge in 0.7 s (miss 0 px)."
    }
  ]
}
```

---

## 4. Conflict Detection Methodology & Risk Rules

Rather than relying on raw distance alone (which causes false positives for diverging or parallel traffic), the module evaluates **Closest Point of Approach (CPA)** and **Time-to-Conflict (TTC)**.

### Mathematical Formulation

1. **Velocity Estimation ($\vec{v}$):**
   * Calculated over a recent observation window (`RECENT_WINDOW_S = 1.5 s`) to capture current heading and speed:
     $$\vec{v} = \left(\frac{x_{\text{end}} - x_{\text{start}}}{\Delta t}, \frac{y_{\text{end}} - y_{\text{start}}}{\Delta t}\right)$$
   * Falls back to the full track if fewer observations exist.

2. **Relative Vectors:**
   * Relative displacement: $\vec{r} = \vec{p}_{\text{vehicle}} - \vec{p}_{\text{pedestrian}}$
   * Relative velocity: $\vec{v}_{\text{rel}} = \vec{v}_{\text{vehicle}} - \vec{v}_{\text{pedestrian}}$

3. **Time to Closest Approach ($t_{\text{CPA}}$):**
   $$t_{\text{CPA}} = -\frac{\vec{r} \cdot \vec{v}_{\text{rel}}}{\|\vec{v}_{\text{rel}}\|^2}$$
   * If $t_{\text{CPA}} \le 0$, the objects are moving away from each other (diverging) $\rightarrow$ No conflict.
   * If $t_{\text{CPA}} > 5.0\text{ s}$, the encounter is too far in the future $\rightarrow$ No conflict.

4. **Miss Distance ($d_{\text{miss}}$):**
   $$\vec{r}_{\text{miss}} = \vec{r} + \vec{v}_{\text{rel}} \cdot t_{\text{CPA}}$$
   $$d_{\text{miss}} = \|\vec{r}_{\text{miss}}\|$$

### Risk Thresholds

| Risk Level | Time-to-Conflict ($t_{\text{CPA}}$) | Miss Distance ($d_{\text{miss}}$) | Condition |
| :--- | :--- | :--- | :--- |
| **HIGH** | $\le 2.0\text{ seconds}$ | $\le 45\text{ pixels}$ | Imminent trajectory intersection |
| **MEDIUM** | $\le 5.0\text{ seconds}$ | $\le 70\text{ pixels}$ | Converging trajectory warranting caution |
| **LOW** | $> 5.0\text{ seconds}$ or $t_{\text{CPA}} \le 0$ | $> 70\text{ pixels}$ | Diverging, parallel, or distant paths |

### Safety Score Calculation

A composite safety score between $0$ and $100$ is provided for the dashboard:
* Starts at $100$ when no conflicts are detected.
* Deducts $25$ per `HIGH` conflict (score capped at $60$).
* Deducts $12$ per `MEDIUM` conflict (score capped at $85$).
* Minor deductions for unconfirmed short tracks ($\le 2$ observations).

---

## 5. Assumptions and Limitations

### Assumptions
1. **Constant Velocity:** Trajectories project straight-line motion at the currently estimated velocity vector.
2. **2D Image Space:** Distances and speeds are measured in pixels and pixel-per-second on the image plane.
3. **Sufficient Frame Rate:** ByteTrack should provide observations at $\ge 10\text{ fps}$ for reliable velocity vectors.

### False-Positive / False-Negative Limitations
* **False Positives:**
  * Pedestrians waiting at curbs or sidewalks near turning vehicles can project a future intersection if the pedestrian stops moving right before entering the road.
  * Curving roads or turn lanes violate straight-line projection.
* **False Negatives:**
  * Rapid, sudden accelerations from stationary vehicles may not be detected early enough if track history is under 2 frames.
  * Heavy visual occlusions dropping track IDs can reset the object history.
* **Perspective Foreshortening:** Objects far from the camera cover fewer pixels per meter than objects close to the camera; pixel-based thresholds represent smaller physical distances in the background.

---

## 6. How to Run & Test

No heavy dependencies required for `ai/prediction.py` (uses standard library `json`, `math`, `pathlib`).

### Run Sample Verification
```bash
python ai/prediction.py
```

### Run Unit Tests
```bash
python -m unittest ai/test_prediction.py
```

### Run with a Custom Track File
```bash
python ai/prediction.py ai/example_tracks.json
```
