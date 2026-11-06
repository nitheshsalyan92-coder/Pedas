"""Conflict detection and risk analysis for pedestrian safety.

Member 4 implementation.
Consumes tracked object records produced by Member 3 (ai.tracking.process_video).
Produces structured risk metrics, conflict events, and alerts for Member 2 (Backend).

Coordinate & Unit Conventions
-----------------------------
- Coordinates (x, y): Bounding-box center in video pixels.
- Time (timestamp): Seconds from the start of the video.
- Speed: Pixels per second.
- Distance: Euclidean distance in pixels between object centroids.

Assumptions & Limitations
-------------------------
1. Perspective distortion: Pixel distances and speeds vary with distance from the camera
   unless camera intrinsics / inverse perspective mapping (IPM) are calibrated.
2. Constant velocity assumption: Short-term trajectory projection assumes linear velocity
   over a 1-3 second horizon.
3. Potential conflicts: The module detects potential movement interference and proximity
   risks, NOT guaranteed collisions.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

# Object categories
PEDESTRIAN_TYPES = {"pedestrian"}
VEHICLE_TYPES = {"car", "motorcycle", "bus", "truck"}

# Proximity and Kinematic Thresholds (in pixels and seconds)
CRITICAL_DISTANCE_PX = 65.0      # Immediate critical proximity threshold
WARNING_DISTANCE_PX = 130.0      # Close proximity threshold
CAUTION_DISTANCE_PX = 190.0      # Cautionary monitoring distance

MIN_CONVERGING_SPEED = 15.0      # Minimum closing speed (px/s) to consider convergence
CRITICAL_TTC_SEC = 1.5           # Time-to-conflict threshold for CRITICAL severity
WARNING_TTC_SEC = 3.0            # Time-to-conflict threshold for WARNING severity
MIN_TRACK_POINTS_FOR_VELOCITY = 2 # Minimum history points to calculate velocity


def analyse_tracks(tracks: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyse object tracks to identify movement conflicts and overall risk.

    Parameters
    ----------
    tracks : list[dict]
        List of object tracking records as returned by ``process_video``.
        Each record must contain: ``object_id``, ``object_type``, ``x``, ``y``,
        ``timestamp``, and optionally ``confidence``, ``bbox``.

    Returns
    -------
    dict
        Structured analysis report matching the shared project data contract:
        - ``pedestrians_detected`` (int): Total unique pedestrians.
        - ``vehicles_detected`` (int): Total unique vehicles.
        - ``conflicts_detected`` (int): Total distinct conflict interactions.
        - ``risk_level`` (str): "LOW", "MEDIUM", or "HIGH".
        - ``alerts`` (list[str]): Human-readable alert messages.
        - ``conflict_details`` (list[dict]): Detailed list of detected conflict events.
        - ``summary`` (dict): Additional metrics (record count, duration, severity counts).
    """
    if not tracks:
        return _empty_result(reason="No tracking records provided.")

    # 1. Group records by object_id (trajectories) and separate types
    trajectories: dict[int, list[dict]] = defaultdict(list)
    pedestrian_ids: set[int] = set()
    vehicle_ids: set[int] = set()
    frames_by_time: dict[float, list[dict]] = defaultdict(list)

    min_time = float("inf")
    max_time = float("-inf")

    for record in tracks:
        obj_id = record.get("object_id")
        obj_type = record.get("object_type", "")
        t = float(record.get("timestamp", 0.0))

        if obj_id is None:
            continue

        trajectories[obj_id].append(record)
        frames_by_time[t].append(record)

        if obj_type in PEDESTRIAN_TYPES:
            pedestrian_ids.add(obj_id)
        elif obj_type in VEHICLE_TYPES:
            vehicle_ids.add(obj_id)

        if t < min_time:
            min_time = t
        if t > max_time:
            max_time = t

    total_pedestrians = len(pedestrian_ids)
    total_vehicles = len(vehicle_ids)
    duration = max(0.0, round(max_time - min_time, 2)) if min_time != float("inf") else 0.0

    # Quick exit if one of the interacting groups is completely absent
    if total_pedestrians == 0 and total_vehicles == 0:
        return _empty_result(
            reason="No pedestrians or vehicles identified in scene.",
            total_records=len(tracks),
            duration=duration,
        )

    if total_vehicles == 0:
        return {
            "pedestrians_detected": total_pedestrians,
            "vehicles_detected": 0,
            "conflicts_detected": 0,
            "risk_level": "LOW",
            "alerts": [
                f"{total_pedestrians} pedestrian(s) observed. No vehicles detected; pedestrian conflict risk is low."
            ],
            "conflict_details": [],
            "summary": {
                "total_records": len(tracks),
                "duration_seconds": duration,
                "critical_conflicts": 0,
                "warning_conflicts": 0,
                "caution_conflicts": 0,
            },
        }

    if total_pedestrians == 0:
        return {
            "pedestrians_detected": 0,
            "vehicles_detected": total_vehicles,
            "conflicts_detected": 0,
            "risk_level": "LOW",
            "alerts": [
                f"{total_vehicles} vehicle(s) observed. No pedestrians detected; conflict risk is low."
            ],
            "conflict_details": [],
            "summary": {
                "total_records": len(tracks),
                "duration_seconds": duration,
                "critical_conflicts": 0,
                "warning_conflicts": 0,
                "caution_conflicts": 0,
            },
        }

    # 2. Compute velocities for each trajectory over time
    velocities = _compute_velocities(trajectories)

    # 3. Detect instantaneous interactions frame by frame
    raw_interactions: list[dict] = []
    # Sort timestamps chronologically
    sorted_times = sorted(frames_by_time.keys())

    for t in sorted_times:
        frame_records = frames_by_time[t]
        peds = [r for r in frame_records if r.get("object_type") in PEDESTRIAN_TYPES]
        vehs = [r for r in frame_records if r.get("object_type") in VEHICLE_TYPES]

        for p in peds:
            p_id = p["object_id"]
            px, py = float(p["x"]), float(p["y"])
            pvx, pvy = velocities.get(p_id, {}).get(t, (0.0, 0.0))
            p_bbox = p.get("bbox")

            for v in vehs:
                v_id = v["object_id"]
                vx, vy = float(v["x"]), float(v["y"])
                vvx, vvy = velocities.get(v_id, {}).get(t, (0.0, 0.0))
                v_bbox = v.get("bbox")

                interaction = _assess_pair(
                    p_id=p_id,
                    v_id=v_id,
                    v_type=v.get("object_type", "vehicle"),
                    timestamp=t,
                    px=px,
                    py=py,
                    pvx=pvx,
                    pvy=pvy,
                    p_bbox=p_bbox,
                    vx=vx,
                    vy=vy,
                    vvx=vvx,
                    vvy=vvy,
                    v_bbox=v_bbox,
                )
                if interaction:
                    raw_interactions.append(interaction)

    # 4. Aggregate frame interactions into distinct multi-frame conflict events
    conflict_events = _aggregate_conflicts(raw_interactions)

    # 5. Evaluate overall risk classification & human-readable alerts
    risk_level, alerts = _classify_risk_and_alerts(
        conflict_events=conflict_events,
        pedestrians_count=total_pedestrians,
        vehicles_count=total_vehicles,
    )

    critical_count = sum(1 for c in conflict_events if c["severity"] == "CRITICAL")
    warning_count = sum(1 for c in conflict_events if c["severity"] == "WARNING")
    caution_count = sum(1 for c in conflict_events if c["severity"] == "CAUTION")

    return {
        "pedestrians_detected": total_pedestrians,
        "vehicles_detected": total_vehicles,
        "conflicts_detected": len(conflict_events),
        "risk_level": risk_level,
        "alerts": alerts,
        "conflict_details": conflict_events,
        "summary": {
            "total_records": len(tracks),
            "duration_seconds": duration,
            "critical_conflicts": critical_count,
            "warning_conflicts": warning_count,
            "caution_conflicts": caution_count,
        },
    }


def _assess_pair(
    p_id: int,
    v_id: int,
    v_type: str,
    timestamp: float,
    px: float,
    py: float,
    pvx: float,
    pvy: float,
    p_bbox: list[float] | None,
    vx: float,
    vy: float,
    vvx: float,
    vvy: float,
    v_bbox: list[float] | None,
) -> dict[str, Any] | None:
    """Evaluate pairwise interaction between one pedestrian and one vehicle at a specific time."""
    dx = px - vx
    dy = py - vy
    dist = math.hypot(dx, dy)

    # Check bounding box overlap if available
    bbox_overlap = False
    if p_bbox and v_bbox and len(p_bbox) == 4 and len(v_bbox) == 4:
        bbox_overlap = _boxes_overlap(p_bbox, v_bbox)

    # Relative velocity (vehicle relative to pedestrian)
    # Vector r is from vehicle to pedestrian: r = (px - vx, py - vy)
    # Vector v_rel is vehicle velocity - pedestrian velocity
    rel_vx = vvx - pvx
    rel_vy = vvy - pvy
    rel_speed = math.hypot(rel_vx, rel_vy)

    # Closing speed: projection of relative velocity onto unit vector towards pedestrian
    # closing_speed = (r . v_rel) / |r|
    # If positive, vehicle and pedestrian are moving closer to each other.
    closing_speed = 0.0
    if dist > 1e-3:
        closing_speed = (dx * rel_vx + dy * rel_vy) / dist

    # Closest Point of Approach (CPA) calculation
    ttc = None
    d_cpa = dist
    if closing_speed > MIN_CONVERGING_SPEED and rel_speed > 1e-2:
        # Time to CPA in seconds
        t_cpa = (dx * rel_vx + dy * rel_vy) / (rel_speed * rel_speed)
        if t_cpa > 0:
            # Future displacement at t_cpa
            future_dx = dx - rel_vx * t_cpa
            future_dy = dy - rel_vy * t_cpa
            d_cpa = math.hypot(future_dx, future_dy)
            # Estimate TTC from closing speed
            ttc = round(dist / closing_speed, 2)

    # Determine severity
    severity = None
    description = ""

    # Rule 1: CRITICAL
    # Immediate high danger: Bounding box overlap, extreme proximity, or converging with TTC <= 1.5s
    if bbox_overlap or dist < CRITICAL_DISTANCE_PX:
        severity = "CRITICAL"
        description = (
            f"Pedestrian #{p_id} and {v_type} #{v_id} in critical proximity ({dist:.1f}px)"
            + (f" with TTC {ttc}s" if ttc else "")
        )
    elif ttc is not None and ttc <= CRITICAL_TTC_SEC and d_cpa < CRITICAL_DISTANCE_PX:
        severity = "CRITICAL"
        description = (
            f"{v_type.capitalize()} #{v_id} rapidly converging towards Pedestrian #{p_id} "
            f"(TTC: {ttc}s, distance: {dist:.1f}px)"
        )

    # Rule 2: WARNING
    # Converging paths with TTC <= 3.0s or within warning proximity
    elif ttc is not None and ttc <= WARNING_TTC_SEC and d_cpa < WARNING_DISTANCE_PX:
        severity = "WARNING"
        description = (
            f"{v_type.capitalize()} #{v_id} converging along path of Pedestrian #{p_id} "
            f"(estimated TTC: {ttc}s, distance: {dist:.1f}px)"
        )
    elif dist < WARNING_DISTANCE_PX and closing_speed > 0:
        severity = "WARNING"
        description = (
            f"Close encounter: Pedestrian #{p_id} and {v_type} #{v_id} converging ({dist:.1f}px)"
        )

    # Rule 3: CAUTION
    # Nearby objects within caution zone
    elif dist < CAUTION_DISTANCE_PX and (closing_speed > 0 or dist < WARNING_DISTANCE_PX):
        severity = "CAUTION"
        description = (
            f"Pedestrian #{p_id} and {v_type} #{v_id} sharing proximity zone ({dist:.1f}px)"
        )

    if not severity:
        return None

    return {
        "pedestrian_id": p_id,
        "vehicle_id": v_id,
        "vehicle_type": v_type,
        "timestamp": timestamp,
        "distance_px": round(dist, 1),
        "closing_speed_px_s": round(closing_speed, 1),
        "ttc_sec": ttc,
        "d_cpa_px": round(d_cpa, 1),
        "severity": severity,
        "description": description,
    }


def _compute_velocities(
    trajectories: dict[int, list[dict]],
) -> dict[int, dict[float, tuple[float, float]]]:
    """Calculate velocity vectors (vx, vy in px/sec) for each object at each timestamp."""
    velocities: dict[int, dict[float, tuple[float, float]]] = defaultdict(dict)

    for obj_id, pts in trajectories.items():
        if len(pts) < MIN_TRACK_POINTS_FOR_VELOCITY:
            for p in pts:
                velocities[obj_id][float(p["timestamp"])] = (0.0, 0.0)
            continue

        # Sort chronologically
        pts_sorted = sorted(pts, key=lambda x: float(x.get("timestamp", 0.0)))
        for i, curr in enumerate(pts_sorted):
            curr_t = float(curr["timestamp"])
            # Use backward difference or nearest forward difference
            if i > 0:
                prev = pts_sorted[i - 1]
                dt = curr_t - float(prev["timestamp"])
                if dt > 1e-4:
                    vx = (float(curr["x"]) - float(prev["x"])) / dt
                    vy = (float(curr["y"]) - float(prev["y"])) / dt
                    velocities[obj_id][curr_t] = (vx, vy)
                else:
                    velocities[obj_id][curr_t] = velocities[obj_id].get(
                        float(prev["timestamp"]), (0.0, 0.0)
                    )
            else:
                next_pt = pts_sorted[1]
                dt = float(next_pt["timestamp"]) - curr_t
                if dt > 1e-4:
                    vx = (float(next_pt["x"]) - float(curr["x"])) / dt
                    vy = (float(next_pt["y"]) - float(curr["y"])) / dt
                    velocities[obj_id][curr_t] = (vx, vy)
                else:
                    velocities[obj_id][curr_t] = (0.0, 0.0)

    return velocities


def _boxes_overlap(box1: list[float], box2: list[float]) -> bool:
    """Check if two bounding boxes [x1, y1, x2, y2] intersect."""
    x1_a, y1_a, x2_a, y2_a = box1
    x1_b, y1_b, x2_b, y2_b = box2
    return not (x2_a < x1_b or x2_b < x1_a or y2_a < y1_b or y2_b < y1_a)


def _aggregate_conflicts(interactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group consecutive frame interactions by (pedestrian_id, vehicle_id) into conflict events."""
    if not interactions:
        return []

    # Group by object pair
    pair_groups: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for inter in interactions:
        key = (inter["pedestrian_id"], inter["vehicle_id"])
        pair_groups[key].append(inter)

    conflict_events: list[dict[str, Any]] = []
    conflict_id = 1

    severity_order = {"CRITICAL": 3, "WARNING": 2, "CAUTION": 1}

    for (p_id, v_id), group in pair_groups.items():
        # Sort by timestamp
        group.sort(key=lambda x: x["timestamp"])

        # Split into distinct episodes if there is a large time gap (> 1.0s)
        episodes: list[list[dict]] = []
        curr_episode = [group[0]]

        for item in group[1:]:
            prev_t = curr_episode[-1]["timestamp"]
            if item["timestamp"] - prev_t <= 1.0:
                curr_episode.append(item)
            else:
                episodes.append(curr_episode)
                curr_episode = [item]
        episodes.append(curr_episode)

        for ep in episodes:
            # Determine peak severity and minimal distance
            highest_sev = max(ep, key=lambda x: severity_order[x["severity"]])["severity"]
            min_dist_item = min(ep, key=lambda x: x["distance_px"])
            ttc_candidates = [x["ttc_sec"] for x in ep if x["ttc_sec"] is not None]
            min_ttc = min(ttc_candidates) if ttc_candidates else None

            start_t = ep[0]["timestamp"]
            end_t = ep[-1]["timestamp"]
            peak_t = min_dist_item["timestamp"]

            conflict_events.append(
                {
                    "conflict_id": conflict_id,
                    "pedestrian_id": p_id,
                    "vehicle_id": v_id,
                    "vehicle_type": ep[0]["vehicle_type"],
                    "severity": highest_sev,
                    "timestamp": round(peak_t, 2),
                    "start_time": round(start_t, 2),
                    "end_time": round(end_t, 2),
                    "min_distance_px": min_dist_item["distance_px"],
                    "estimated_ttc_sec": min_ttc,
                    "description": min_dist_item["description"],
                }
            )
            conflict_id += 1

    # Sort conflicts chronologically by start time
    conflict_events.sort(key=lambda x: x["start_time"])
    return conflict_events


def _classify_risk_and_alerts(
    conflict_events: list[dict[str, Any]],
    pedestrians_count: int,
    vehicles_count: int,
) -> tuple[str, list[str]]:
    """Determine explainable LOW/MEDIUM/HIGH risk level and produce human-readable alerts."""
    critical_events = [c for c in conflict_events if c["severity"] == "CRITICAL"]
    warning_events = [c for c in conflict_events if c["severity"] == "WARNING"]
    caution_events = [c for c in conflict_events if c["severity"] == "CAUTION"]

    alerts: list[str] = []

    # Risk level classification rules:
    # HIGH: Any critical conflict, or multiple warnings
    if len(critical_events) > 0 or len(warning_events) >= 2:
        risk_level = "HIGH"
        alerts.append(
            f"HIGH RISK: {len(critical_events)} critical and {len(warning_events)} warning "
            f"movement conflict(s) detected between pedestrians and vehicles."
        )
        for c in critical_events[:3]:  # Top 3 critical highlights
            alerts.append(
                f"Critical conflict: Pedestrian #{c['pedestrian_id']} and {c['vehicle_type']} #{c['vehicle_id']} "
                f"at t={c['timestamp']}s (min dist: {c['min_distance_px']}px"
                + (f", TTC: {c['estimated_ttc_sec']}s" if c['estimated_ttc_sec'] else "")
                + ")."
            )

    # MEDIUM: At least 1 warning conflict or multiple cautions
    elif len(warning_events) > 0 or len(caution_events) >= 2:
        risk_level = "MEDIUM"
        alerts.append(
            f"MEDIUM RISK: {len(warning_events)} warning conflict(s) detected. "
            f"Safe margins narrowed between road users."
        )
        for w in warning_events[:2]:
            alerts.append(
                f"Warning: Pedestrian #{w['pedestrian_id']} and {w['vehicle_type']} #{w['vehicle_id']} "
                f"approached within {w['min_distance_px']}px at t={w['timestamp']}s."
            )

    # LOW: Safe conditions, or only isolated cautions
    else:
        risk_level = "LOW"
        if len(caution_events) == 1:
            alerts.append(
                f"LOW RISK: 1 cautionary encounter observed, but safe distances were generally maintained."
            )
        else:
            alerts.append(
                f"LOW RISK: Safe distances maintained between {pedestrians_count} pedestrian(s) "
                f"and {vehicles_count} vehicle(s)."
            )

    return risk_level, alerts


def _empty_result(
    reason: str,
    total_records: int = 0,
    duration: float = 0.0,
) -> dict[str, Any]:
    """Helper to return a well-formed zero-result payload."""
    return {
        "pedestrians_detected": 0,
        "vehicles_detected": 0,
        "conflicts_detected": 0,
        "risk_level": "LOW",
        "alerts": [reason],
        "conflict_details": [],
        "summary": {
            "total_records": total_records,
            "duration_seconds": duration,
            "critical_conflicts": 0,
            "warning_conflicts": 0,
            "caution_conflicts": 0,
        },
    }


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 2:
        print("usage: python -m ai.prediction <tracks.json>", file=sys.stderr)
        raise SystemExit(2)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        tracks_data = json.load(f)

    result = analyse_tracks(tracks_data)
    print(json.dumps(result, indent=2))
