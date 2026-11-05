"""Rule-based pedestrian-vehicle conflict risk analysis.

Input is a flat list of track observations. Member 3 can supply real detections
without changing the interface or this function signature.

Each observation:
    object_id (int): ByteTrack identity.
    object_type (str): "pedestrian" or "person"; vehicles are "car", "bus", "truck",
                       "motorcycle", or "vehicle".
    x, y (float): Bounding-box centre in video pixels (origin top-left).
    timestamp (float): Seconds from the start of the video.
    confidence (float, optional): Detection confidence score.
    bbox (list, optional): [x1, y1, x2, y2] bounding box coordinates.

Assumptions:
- Trajectory velocity is estimated over a recent sliding window (default: 1.5 s)
  to capture current direction and speed, with fallback to full track for shorter observations.
- Future trajectory assumes constant straight-line motion at the estimated velocity.
- Conflict detection evaluates Closest Point of Approach (CPA) using relative vectors.
- A conflict requires paths to converge in the future (Time-to-Conflict > 0).
- Proximity alone is not sufficient; separating or parallel objects are marked LOW risk.
- HIGH: approach within 2.0 s and miss distance <= 45 px.
- MEDIUM: approach within 5.0 s and miss distance <= 70 px.
- LOW: paths diverge, parallel, or closest approach > 5.0 s.
- Disclaimer: This flags potential conflicts for safety monitoring. It does not predict
  accidents with certainty.
"""

import json
import sys
from math import hypot
from pathlib import Path

VEHICLE_TYPES = {"car", "bus", "truck", "motorcycle", "vehicle"}
PEDESTRIAN_TYPES = {"pedestrian", "person"}

HIGH_TTC_S = 2.0
MEDIUM_TTC_S = 5.0
HIGH_MISS_PX = 45.0
MEDIUM_MISS_PX = 70.0
MIN_RELATIVE_SPEED_PX_S = 1.0
RECENT_WINDOW_S = 1.5


def analyse_tracks(tracks):
    """Return counts, conflict records, a risk level, a safety score, and alerts.

    Args:
        tracks: A list of track observations, or a dict containing {"tracks": [...]}.

    Returns:
        A dict matching the shared data contract with keys:
            - pedestrians_detected (int)
            - vehicles_detected (int)
            - conflicts_detected (int)
            - risk_level (str: "LOW", "MEDIUM", "HIGH")
            - safety_score (int: 0-100)
            - alerts (list[str])
            - conflicts (list[dict])
    """
    if isinstance(tracks, dict) and isinstance(tracks.get("tracks"), list):
        tracks = tracks["tracks"]
    if not isinstance(tracks, list):
        return _empty_result("No tracking data provided.")
    if len(tracks) == 0:
        return _empty_result("No tracking data provided.")

    grouped = _group_observations(tracks)
    if not grouped:
        return _empty_result("No usable track points were found.")

    pedestrians = []
    vehicles = []
    short_tracks = 0

    for identity, points in grouped.items():
        kind = _classify(points[-1]["object_type"])
        if kind is None:
            continue
        motion = _motion(points)
        record = {
            "object_id": identity,
            "object_type": points[-1]["object_type"],
            "x": points[-1]["x"],
            "y": points[-1]["y"],
            "velocity": None if motion is None else motion[0],
            "speed_px_s": None if motion is None else round(motion[1], 1),
        }
        if motion is None:
            short_tracks += 1
        if kind == "pedestrian":
            pedestrians.append(record)
        else:
            vehicles.append(record)

    conflicts = []
    for pedestrian in pedestrians:
        for vehicle in vehicles:
            conflict = _pair_conflict(pedestrian, vehicle)
            if conflict is not None:
                conflicts.append(conflict)

    risk_level = _overall_risk(conflicts)
    alerts = _alerts(conflicts, short_tracks, pedestrians, vehicles)
    safety_score = _calculate_safety_score(conflicts, short_tracks)

    return {
        "pedestrians_detected": len(pedestrians),
        "vehicles_detected": len(vehicles),
        "conflicts_detected": len(conflicts),
        "risk_level": risk_level,
        "safety_score": safety_score,
        "alerts": alerts,
        "conflicts": conflicts,
    }


def _empty_result(message):
    return {
        "pedestrians_detected": 0,
        "vehicles_detected": 0,
        "conflicts_detected": 0,
        "risk_level": "LOW",
        "safety_score": 100,
        "alerts": [message],
        "conflicts": [],
    }


def _calculate_safety_score(conflicts, short_tracks=0):
    """Compute a 0-100 safety score to support dashboard metrics.

    100 indicates optimal safety (no conflicts detected).
    HIGH conflicts cause significant reductions (base cap 60).
    MEDIUM conflicts cause moderate reductions (base cap 85).
    """
    if not conflicts:
        deduction = min(short_tracks * 2, 10)
        return max(0, 100 - deduction)

    high_count = sum(1 for c in conflicts if c.get("risk_level") == "HIGH")
    medium_count = sum(1 for c in conflicts if c.get("risk_level") == "MEDIUM")

    score = 100 - (high_count * 25) - (medium_count * 12) - min(short_tracks, 5)

    if high_count > 0:
        score = min(score, 60)
    elif medium_count > 0:
        score = min(score, 85)

    return max(0, min(100, score))


def _group_observations(tracks):
    grouped = {}
    for raw in tracks:
        point = _clean_point(raw)
        if point is None:
            continue
        grouped.setdefault(point["object_id"], []).append(point)
    for points in grouped.values():
        points.sort(key=lambda item: item["timestamp"])
    return grouped


def _clean_point(raw):
    if not isinstance(raw, dict):
        return None
    try:
        return {
            "object_id": raw["object_id"],
            "object_type": str(raw["object_type"]).strip().lower(),
            "x": float(raw["x"]),
            "y": float(raw["y"]),
            "timestamp": float(raw["timestamp"]),
        }
    except (KeyError, TypeError, ValueError):
        return None


def _classify(object_type):
    if object_type in PEDESTRIAN_TYPES:
        return "pedestrian"
    if object_type in VEHICLE_TYPES:
        return "vehicle"
    return None


def _motion(points, recent_window_s=RECENT_WINDOW_S):
    """Return ((vx, vy), speed_px_s) using recent points, or None when track is too short."""
    if len(points) < 2:
        return None

    last_time = points[-1]["timestamp"]
    cutoff = last_time - recent_window_s
    recent = [p for p in points if p["timestamp"] >= cutoff]
    if len(recent) < 2:
        recent = points[-2:]

    start = recent[0]
    end = recent[-1]
    dt = end["timestamp"] - start["timestamp"]
    if dt <= 0:
        dt = points[-1]["timestamp"] - points[0]["timestamp"]
        if dt <= 0:
            return None
        start = points[0]
        end = points[-1]

    vx = (end["x"] - start["x"]) / dt
    vy = (end["y"] - start["y"]) / dt
    speed = hypot(vx, vy)
    return ((vx, vy), speed)


def _pair_conflict(pedestrian, vehicle):
    if pedestrian["velocity"] is None or vehicle["velocity"] is None:
        return None

    rx = vehicle["x"] - pedestrian["x"]
    ry = vehicle["y"] - pedestrian["y"]
    rvx = vehicle["velocity"][0] - pedestrian["velocity"][0]
    rvy = vehicle["velocity"][1] - pedestrian["velocity"][1]
    speed_sq = rvx * rvx + rvy * rvy
    if speed_sq < MIN_RELATIVE_SPEED_PX_S * MIN_RELATIVE_SPEED_PX_S:
        return None

    time_to_closest = -((rx * rvx) + (ry * rvy)) / speed_sq
    if time_to_closest < 0 or time_to_closest > MEDIUM_TTC_S:
        return None

    miss_x = rx + rvx * time_to_closest
    miss_y = ry + rvy * time_to_closest
    miss_distance = hypot(miss_x, miss_y)
    current_distance = hypot(rx, ry)
    pair_risk = _pair_risk(time_to_closest, miss_distance)
    if pair_risk is None:
        return None

    closing_speed = current_distance / time_to_closest if time_to_closest > 0 else 0.0
    return {
        "pedestrian_id": pedestrian["object_id"],
        "vehicle_id": vehicle["object_id"],
        "distance_px": round(current_distance, 1),
        "miss_distance_px": round(miss_distance, 1),
        "closing_speed_px_s": round(closing_speed, 1),
        "time_to_conflict_s": round(time_to_closest, 2),
        "risk_level": pair_risk,
        "reason": (
            f"Pedestrian {pedestrian['object_id']} and vehicle {vehicle['object_id']} "
            f"are {current_distance:.0f} px apart and their paths converge in "
            f"{time_to_closest:.1f} s (miss {miss_distance:.0f} px)."
        ),
    }


def _pair_risk(time_to_closest, miss_distance):
    if time_to_closest <= HIGH_TTC_S and miss_distance <= HIGH_MISS_PX:
        return "HIGH"
    if time_to_closest <= MEDIUM_TTC_S and miss_distance <= MEDIUM_MISS_PX:
        return "MEDIUM"
    return None


def _overall_risk(conflicts):
    levels = {item["risk_level"] for item in conflicts}
    if "HIGH" in levels:
        return "HIGH"
    if "MEDIUM" in levels:
        return "MEDIUM"
    return "LOW"


def _alerts(conflicts, short_tracks, pedestrians, vehicles):
    alerts = [item["reason"] for item in conflicts]
    if short_tracks and not conflicts:
        alerts.append(
            "Not enough track history to estimate direction or speed "
            f"for {short_tracks} object(s)."
        )
    elif short_tracks:
        alerts.append(
            f"{short_tracks} object(s) were ignored because they have fewer than 2 positions."
        )
    if not alerts:
        if not pedestrians or not vehicles:
            alerts.append("No pedestrian-vehicle pair was available to compare.")
        else:
            alerts.append("No pedestrian-vehicle conflict detected.")
    return alerts


def analyse_track_file(path):
    """Load a JSON track file and return the same result as analyse_tracks."""
    file_path = Path(path)
    with file_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    return analyse_tracks(payload)


def analyse_video(video_path, **kwargs):
    """Run Member 3's process_video, then score the tracks.

    ai.tracking lives on the detection branch. This raises a clear error
    until that branch is merged into this one.
    """
    try:
        from ai.tracking import process_video
    except ImportError as exc:
        raise RuntimeError(
            "ai.tracking is not available yet. Use analyse_tracks(tracks) "
            "until the detection branch is merged."
        ) from exc
    return analyse_tracks(process_video(video_path, **kwargs))


def _load_samples():
    sample_path = Path(__file__).with_name("sample_tracks.json")
    with sample_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _run_sample_checks():
    samples = _load_samples()
    expected = {
        "far_apart": "LOW",
        "separating_but_close": "LOW",
        "parallel_miss": "LOW",
        "meets_after_five_seconds": "LOW",
        "converging_medium": "MEDIUM",
        "converging_high": "HIGH",
        "too_short": "LOW",
        "empty": "LOW",
    }
    for name, tracks in samples.items():
        result = analyse_tracks(tracks)
        print(f"[{name}] {result['risk_level']} conflicts={result['conflicts_detected']} safety_score={result.get('safety_score')}")
        for alert in result["alerts"]:
            print(f"  - {alert}")
        if result["risk_level"] != expected[name]:
            raise SystemExit(f"{name} expected {expected[name]}, got {result['risk_level']}")
        if name == "empty" and result["pedestrians_detected"] != 0:
            raise SystemExit("empty input should not count objects")
        if name == "too_short" and result["conflicts_detected"] != 0:
            raise SystemExit("a single position must not create a conflict")
    member3_shape = []
    for point in samples["converging_high"]:
        record = dict(point)
        record["bbox"] = [record["x"] - 10, record["y"] - 20, record["x"] + 10, record["y"] + 20]
        member3_shape.append(record)
    if analyse_tracks(member3_shape)["risk_level"] != "HIGH":
        raise SystemExit("Member 3 records with bbox should still score HIGH")
    try:
        analyse_video("missing.mp4")
    except RuntimeError as exc:
        if "ai.tracking" not in str(exc):
            raise
    else:
        raise SystemExit("analyse_video should explain that tracking is not merged yet")
    example = analyse_tracks(samples["converging_high"])
    example_path = Path(__file__).with_name("example_result.json")
    example_path.write_text(json.dumps(example, indent=2) + "\n", encoding="utf-8")
    print("sample checks passed")
    print(f"wrote {example_path.name}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(json.dumps(analyse_track_file(sys.argv[1]), indent=2))
    else:
        _run_sample_checks()
