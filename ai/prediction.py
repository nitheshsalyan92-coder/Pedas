"""Conflict detection and risk analysis for pedestrian safety (Member 4).

Consumes tracked object records produced by Member 3 (ai.tracking.process_video).
Produces structured risk metrics, conflict events, and alerts for Member 2 (Backend)
and Member 1 (Frontend).

Coordinate & Unit Conventions
-----------------------------
- Coordinates (x, y): Bounding-box center in video pixels.
- Time (timestamp): Seconds from the start of the video.
- Speed: Pixels per second.
- Distance: Euclidean distance in pixels between object centroids.

Assumptions & Limitations
-------------------------
1. Trajectory velocity is estimated using instantaneous and sliding-window methods.
2. Short-term trajectory projection assumes constant velocity over a 1-3 second horizon.
3. Conflict detection evaluates Closest Point of Approach (CPA) using relative vectors.
4. Identifies potential conflicts; does not predict guaranteed accidents.
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Object categories
PEDESTRIAN_TYPES = {"pedestrian", "person"}
VEHICLE_TYPES = {"car", "motorcycle", "bus", "truck", "vehicle"}

# Kinematic and Proximity Thresholds
CRITICAL_DISTANCE_PX = 65.0      # Immediate critical proximity threshold
WARNING_DISTANCE_PX = 130.0      # Close proximity threshold
CAUTION_DISTANCE_PX = 190.0      # Cautionary monitoring distance

CRITICAL_TTC_SEC = 1.5           # Time-to-conflict threshold for HIGH / CRITICAL
WARNING_TTC_SEC = 5.0            # Time-to-conflict threshold for MEDIUM / WARNING
CRITICAL_MISS_PX = 50.0          # Max miss distance at CPA for HIGH / CRITICAL
WARNING_MISS_PX = 70.0           # Max miss distance at CPA for MEDIUM / WARNING

HIGH_TTC_S = CRITICAL_TTC_SEC
MEDIUM_TTC_S = WARNING_TTC_SEC
HIGH_MISS_PX = 45.0
MEDIUM_MISS_PX = 70.0
MIN_RELATIVE_SPEED_PX_S = 1.0
RECENT_WINDOW_S = 1.5


def analyse_tracks(tracks: Any) -> dict[str, Any]:
    """Analyse object tracks to identify movement conflicts and overall risk.

    Parameters
    ----------
    tracks : list[dict] | dict
        List of object tracking records as returned by ``process_video``,
        or a dict wrapper ``{"tracks": [...]}``. Each record contains:
        ``object_id``, ``object_type``, ``x``, ``y``, ``timestamp``,
        and optionally ``confidence``, ``bbox``.

    Returns
    -------
    dict
        Structured analysis report matching the shared data contract:
        - ``pedestrians_detected`` (int)
        - ``vehicles_detected`` (int)
        - ``conflicts_detected`` (int)
        - ``risk_level`` (str): "LOW", "MEDIUM", or "HIGH"
        - ``safety_score`` (int): 0-100 composite safety score
        - ``alerts`` (list[str]): Human-readable alert messages
        - ``conflicts`` (list[dict]): Detailed conflict events
        - ``conflict_details`` (list[dict]): Alias for conflict events
        - ``summary`` (dict): Scene overview statistics
    """
    if isinstance(tracks, dict) and isinstance(tracks.get("tracks"), list):
        tracks = tracks["tracks"]
    if not isinstance(tracks, list) or len(tracks) == 0:
        return _empty_result("No tracking records provided.")

    # 1. Group records by object_id (trajectories) and separate categories
    trajectories: dict[int, list[dict]] = defaultdict(list)
    frames_by_time: dict[float, list[dict]] = defaultdict(list)
    pedestrian_ids: set[int] = set()
    vehicle_ids: set[int] = set()

    min_time = float("inf")
    max_time = float("-inf")

    for raw in tracks:
        point = _clean_point(raw)
        if point is None:
            continue
        obj_id = point["object_id"]
        obj_type = point["object_type"]
        t = point["timestamp"]

        trajectories[obj_id].append(point)
        frames_by_time[t].append(point)

        kind = _classify(obj_type)
        if kind == "pedestrian":
            pedestrian_ids.add(obj_id)
        elif kind == "vehicle":
            vehicle_ids.add(obj_id)

        if t < min_time:
            min_time = t
        if t > max_time:
            max_time = t

    total_pedestrians = len(pedestrian_ids)
    total_vehicles = len(vehicle_ids)
    duration = max(0.0, round(max_time - min_time, 2)) if min_time != float("inf") else 0.0

    if total_pedestrians == 0 and total_vehicles == 0:
        return _empty_result(
            "No usable track points were found.",
            total_records=len(tracks),
            duration=duration,
        )

    if total_vehicles == 0:
        short_count = sum(1 for pts in trajectories.values() if len(pts) < 2)
        alerts = [
            f"{total_pedestrians} pedestrian(s) observed. No vehicles detected; pedestrian conflict risk is low."
        ]
        if short_count:
            alerts.append(f"Not enough track history to estimate direction or speed for {short_count} object(s).")
        return {
            "pedestrians_detected": total_pedestrians,
            "vehicles_detected": 0,
            "conflicts_detected": 0,
            "risk_level": "LOW",
            "safety_score": max(0, 100 - min(short_count * 2, 10)),
            "alerts": alerts,
            "conflicts": [],
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
            "safety_score": 100,
            "alerts": [
                f"{total_vehicles} vehicle(s) observed. No pedestrians detected; conflict risk is low."
            ],
            "conflicts": [],
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
    short_tracks = sum(1 for pts in trajectories.values() if len(pts) < 2)

    # 3. Detect instantaneous pairwise interactions frame-by-frame
    raw_interactions: list[dict] = []
    sorted_times = sorted(frames_by_time.keys())

    for t in sorted_times:
        frame_records = frames_by_time[t]
        peds = [r for r in frame_records if _classify(r.get("object_type", "")) == "pedestrian"]
        vehs = [r for r in frame_records if _classify(r.get("object_type", "")) == "vehicle"]

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
        short_tracks=short_tracks,
    )

    critical_count = sum(1 for c in conflict_events if c["severity"] == "CRITICAL")
    warning_count = sum(1 for c in conflict_events if c["severity"] == "WARNING")
    caution_count = sum(1 for c in conflict_events if c["severity"] == "CAUTION")

    counted_conflicts = [c for c in conflict_events if c["severity"] in {"CRITICAL", "WARNING"}]
    conflicts_detected = len(counted_conflicts) if counted_conflicts else len(conflict_events)

    safety_score = _calculate_safety_score(conflict_events, short_tracks)

    return {
        "pedestrians_detected": total_pedestrians,
        "vehicles_detected": total_vehicles,
        "conflicts_detected": conflicts_detected,
        "risk_level": risk_level,
        "safety_score": safety_score,
        "alerts": alerts,
        "conflicts": conflict_events,
        "conflict_details": conflict_events,
        "summary": {
            "total_records": len(tracks),
            "duration_seconds": duration,
            "critical_conflicts": critical_count,
            "warning_conflicts": warning_count,
            "caution_conflicts": caution_count,
        },
    }


def _clean_point(raw: Any) -> dict[str, Any] | None:
    """Validate and sanitize a single tracking observation."""
    if not isinstance(raw, dict):
        return None
    try:
        cleaned = {
            "object_id": raw["object_id"],
            "object_type": str(raw["object_type"]).strip().lower(),
            "x": float(raw["x"]),
            "y": float(raw["y"]),
            "timestamp": float(raw["timestamp"]),
        }
        if "confidence" in raw and raw["confidence"] is not None:
            cleaned["confidence"] = float(raw["confidence"])
        if "bbox" in raw and isinstance(raw["bbox"], list) and len(raw["bbox"]) == 4:
            cleaned["bbox"] = [float(v) for v in raw["bbox"]]
        return cleaned
    except (KeyError, TypeError, ValueError):
        return None


def _classify(object_type: str) -> str | None:
    """Classify road user type into pedestrian or vehicle."""
    normalized = str(object_type).strip().lower()
    if normalized in PEDESTRIAN_TYPES:
        return "pedestrian"
    if normalized in VEHICLE_TYPES:
        return "vehicle"
    return None


def _motion(points: list[dict], recent_window_s: float = RECENT_WINDOW_S) -> tuple[tuple[float, float], float] | None:
    """Return ((vx, vy), speed_px_s) using recent points, or None when track is too short."""
    if not points or len(points) < 2:
        return None

    last_time = float(points[-1]["timestamp"])
    cutoff = last_time - recent_window_s
    recent = [p for p in points if float(p["timestamp"]) >= cutoff]
    if len(recent) < 2:
        recent = points[-2:]

    start = recent[0]
    end = recent[-1]
    dt = float(end["timestamp"]) - float(start["timestamp"])
    if dt <= 0:
        dt = float(points[-1]["timestamp"]) - float(points[0]["timestamp"])
        if dt <= 0:
            return None
        start = points[0]
        end = points[-1]

    vx = (float(end["x"]) - float(start["x"])) / dt
    vy = (float(end["y"]) - float(start["y"])) / dt
    speed = math.hypot(vx, vy)
    return ((vx, vy), speed)


def _compute_velocities(
    trajectories: dict[int, list[dict]],
) -> dict[int, dict[float, tuple[float, float]]]:
    """Calculate velocity vectors (vx, vy in px/sec) for each object at each timestamp."""
    velocities: dict[int, dict[float, tuple[float, float]]] = defaultdict(dict)

    for obj_id, pts in trajectories.items():
        if len(pts) < 2:
            for p in pts:
                velocities[obj_id][float(p["timestamp"])] = (0.0, 0.0)
            continue

        pts_sorted = sorted(pts, key=lambda x: float(x.get("timestamp", 0.0)))
        full_motion = _motion(pts_sorted)
        global_v = full_motion[0] if full_motion else (0.0, 0.0)

        for i, curr in enumerate(pts_sorted):
            curr_t = float(curr["timestamp"])
            if len(pts_sorted) == 2:
                velocities[obj_id][curr_t] = global_v
                continue

            if i > 0:
                prev = pts_sorted[i - 1]
                dt = curr_t - float(prev["timestamp"])
                if dt > 1e-4:
                    vx = (float(curr["x"]) - float(prev["x"])) / dt
                    vy = (float(curr["y"]) - float(prev["y"])) / dt
                    velocities[obj_id][curr_t] = (vx, vy)
                else:
                    velocities[obj_id][curr_t] = velocities[obj_id].get(
                        float(prev["timestamp"]), global_v
                    )
            else:
                next_pt = pts_sorted[1]
                dt = float(next_pt["timestamp"]) - curr_t
                if dt > 1e-4:
                    vx = (float(next_pt["x"]) - float(curr["x"])) / dt
                    vy = (float(next_pt["y"]) - float(curr["y"])) / dt
                    velocities[obj_id][curr_t] = (vx, vy)
                else:
                    velocities[obj_id][curr_t] = global_v

    return velocities


def _boxes_overlap(box1: list[float], box2: list[float]) -> bool:
    """Check if two bounding boxes [x1, y1, x2, y2] intersect."""
    x1_a, y1_a, x2_a, y2_a = box1
    x1_b, y1_b, x2_b, y2_b = box2
    return not (x2_a < x1_b or x2_b < x1_a or y2_a < y1_b or y2_b < y1_a)


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
    dx = vx - px
    dy = vy - py
    dist = math.hypot(dx, dy)

    # Check bounding box overlap
    bbox_overlap = False
    if p_bbox and v_bbox and len(p_bbox) == 4 and len(v_bbox) == 4:
        bbox_overlap = _boxes_overlap(p_bbox, v_bbox)

    rvx = vvx - pvx
    rvy = vvy - pvy
    speed_sq = rvx * rvx + rvy * rvy

    closing_speed = 0.0
    if dist > 1e-3:
        closing_speed = -((dx * rvx + dy * rvy) / dist)

    time_to_closest = None
    miss_distance = dist

    if speed_sq >= MIN_RELATIVE_SPEED_PX_S * MIN_RELATIVE_SPEED_PX_S:
        t_cpa = -((dx * rvx) + (dy * rvy)) / speed_sq
        if t_cpa > 0:
            miss_x = dx + rvx * t_cpa
            miss_y = dy + rvy * t_cpa
            miss_distance = math.hypot(miss_x, miss_y)
            time_to_closest = t_cpa

    severity = None
    risk_level = None
    description = ""

    # Rule 1: CRITICAL / HIGH
    if bbox_overlap:
        severity = "CRITICAL"
        risk_level = "HIGH"
        description = f"Critical conflict: Pedestrian {p_id} and {v_type} {v_id} bounding boxes overlap."
    elif time_to_closest is not None and time_to_closest <= 1.5 and miss_distance <= 50.0:
        severity = "CRITICAL"
        risk_level = "HIGH"
        description = (
            f"Pedestrian {p_id} and {v_type} {v_id} are {dist:.0f} px apart "
            f"and their paths converge in {time_to_closest:.1f} s (miss {miss_distance:.0f} px)."
        )
    elif dist < 50.0 and (closing_speed > 5.0 or (time_to_closest is not None and time_to_closest <= 1.5)):
        severity = "CRITICAL"
        risk_level = "HIGH"
        ttc_str = f" in {time_to_closest:.1f} s" if time_to_closest is not None else ""
        description = f"Pedestrian {p_id} and {v_type} {v_id} in critical proximity ({dist:.0f} px){ttc_str}."

    # Rule 2: WARNING / MEDIUM
    elif (
        time_to_closest is not None
        and time_to_closest <= 5.0
        and miss_distance <= 70.0
    ):
        severity = "WARNING"
        risk_level = "MEDIUM"
        description = (
            f"Pedestrian {p_id} and {v_type} {v_id} are {dist:.0f} px apart "
            f"and their paths converge in {time_to_closest:.1f} s (miss {miss_distance:.0f} px)."
        )
    elif dist < 130.0 and closing_speed > 10.0 and (time_to_closest is not None and time_to_closest <= 3.0):
        severity = "WARNING"
        risk_level = "MEDIUM"
        description = f"Close encounter: Pedestrian {p_id} and {v_type} {v_id} converging ({dist:.0f} px)."
    elif dist <= 50.0:
        # Close buffer proximity
        severity = "WARNING"
        risk_level = "MEDIUM"
        description = f"Close encounter: Pedestrian {p_id} and {v_type} {v_id} within {dist:.0f} px."

    if not severity:
        return None

    return {
        "pedestrian_id": p_id,
        "vehicle_id": v_id,
        "vehicle_type": v_type,
        "timestamp": timestamp,
        "distance_px": round(dist, 1),
        "miss_distance_px": round(miss_distance, 1),
        "closing_speed_px_s": round(closing_speed, 1),
        "time_to_conflict_s": round(time_to_closest, 2) if time_to_closest is not None else None,
        "estimated_ttc_sec": round(time_to_closest, 2) if time_to_closest is not None else None,
        "severity": severity,
        "risk_level": risk_level,
        "description": description,
        "reason": description,
    }


def _pair_conflict(pedestrian: dict, vehicle: dict) -> dict[str, Any] | None:
    """Direct single-pair conflict assessment for point records with velocity."""
    if pedestrian.get("velocity") is None or vehicle.get("velocity") is None:
        return None

    rx = float(vehicle["x"]) - float(pedestrian["x"])
    ry = float(vehicle["y"]) - float(pedestrian["y"])
    rvx = float(vehicle["velocity"][0]) - float(pedestrian["velocity"][0])
    rvy = float(vehicle["velocity"][1]) - float(pedestrian["velocity"][1])
    speed_sq = rvx * rvx + rvy * rvy

    if speed_sq < MIN_RELATIVE_SPEED_PX_S * MIN_RELATIVE_SPEED_PX_S:
        return None

    time_to_closest = -((rx * rvx) + (ry * rvy)) / speed_sq
    if time_to_closest < 0 or time_to_closest > MEDIUM_TTC_S:
        return None

    miss_x = rx + rvx * time_to_closest
    miss_y = ry + rvy * time_to_closest
    miss_distance = math.hypot(miss_x, miss_y)
    current_distance = math.hypot(rx, ry)

    pair_risk = _pair_risk(time_to_closest, miss_distance)
    if pair_risk is None:
        return None

    closing_speed = current_distance / time_to_closest if time_to_closest > 0 else 0.0
    reason = (
        f"Pedestrian {pedestrian['object_id']} and vehicle {vehicle['object_id']} "
        f"are {current_distance:.0f} px apart and their paths converge in "
        f"{time_to_closest:.1f} s (miss {miss_distance:.0f} px)."
    )

    return {
        "pedestrian_id": pedestrian["object_id"],
        "vehicle_id": vehicle["object_id"],
        "distance_px": round(current_distance, 1),
        "miss_distance_px": round(miss_distance, 1),
        "closing_speed_px_s": round(closing_speed, 1),
        "time_to_conflict_s": round(time_to_closest, 2),
        "estimated_ttc_sec": round(time_to_closest, 2),
        "risk_level": pair_risk,
        "severity": "CRITICAL" if pair_risk == "HIGH" else "WARNING",
        "reason": reason,
        "description": reason,
    }


def _pair_risk(time_to_closest: float, miss_distance: float) -> str | None:
    if time_to_closest <= 1.5 and miss_distance <= HIGH_MISS_PX:
        return "HIGH"
    if time_to_closest <= MEDIUM_TTC_S and miss_distance <= MEDIUM_MISS_PX:
        return "MEDIUM"
    return None


def _aggregate_conflicts(interactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group consecutive frame interactions by (pedestrian_id, vehicle_id) into distinct events."""
    if not interactions:
        return []

    pair_groups: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for inter in interactions:
        key = (inter["pedestrian_id"], inter["vehicle_id"])
        pair_groups[key].append(inter)

    conflict_events: list[dict[str, Any]] = []
    conflict_id = 1
    severity_order = {"CRITICAL": 3, "WARNING": 2, "CAUTION": 1}

    for (p_id, v_id), group in pair_groups.items():
        group.sort(key=lambda x: x["timestamp"])

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
            has_convergence = any(x["time_to_conflict_s"] is not None for x in ep) or any(x["closing_speed_px_s"] > 0 for x in ep)
            if not has_convergence and len(ep) < 3:
                continue

            highest_sev = max(ep, key=lambda x: severity_order.get(x["severity"], 1))["severity"]
            min_dist_item = min(ep, key=lambda x: x["distance_px"])
            ttc_candidates = [x["time_to_conflict_s"] for x in ep if x["time_to_conflict_s"] is not None]
            min_ttc = min(ttc_candidates) if ttc_candidates else None

            start_t = ep[0]["timestamp"]
            end_t = ep[-1]["timestamp"]
            peak_t = min_dist_item["timestamp"]

            risk_level = "HIGH" if highest_sev == "CRITICAL" else ("MEDIUM" if highest_sev == "WARNING" else "LOW")

            conflict_events.append(
                {
                    "conflict_id": conflict_id,
                    "pedestrian_id": p_id,
                    "vehicle_id": v_id,
                    "vehicle_type": ep[0].get("vehicle_type", "vehicle"),
                    "severity": highest_sev,
                    "risk_level": risk_level,
                    "timestamp": round(peak_t, 2),
                    "start_time": round(start_t, 2),
                    "end_time": round(end_t, 2),
                    "min_distance_px": min_dist_item["distance_px"],
                    "distance_px": min_dist_item["distance_px"],
                    "miss_distance_px": min_dist_item.get("miss_distance_px", 0.0),
                    "closing_speed_px_s": min_dist_item.get("closing_speed_px_s", 0.0),
                    "time_to_conflict_s": min_ttc,
                    "estimated_ttc_sec": min_ttc,
                    "description": min_dist_item["description"],
                    "reason": min_dist_item["reason"],
                }
            )
            conflict_id += 1

    conflict_events.sort(key=lambda x: x["start_time"])
    return conflict_events


def _classify_risk_and_alerts(
    conflict_events: list[dict[str, Any]],
    pedestrians_count: int,
    vehicles_count: int,
    short_tracks: int = 0,
) -> tuple[str, list[str]]:
    """Determine explainable LOW/MEDIUM/HIGH risk level and produce human-readable alerts."""
    critical_events = [c for c in conflict_events if c["severity"] == "CRITICAL"]
    warning_events = [c for c in conflict_events if c["severity"] == "WARNING"]
    caution_events = [c for c in conflict_events if c["severity"] == "CAUTION"]

    alerts: list[str] = []

    # HIGH risk
    if len(critical_events) > 0 or len(warning_events) >= 2:
        risk_level = "HIGH"
        for c in critical_events:
            alerts.append(c["reason"])
        for w in warning_events:
            alerts.append(w["reason"])

    # MEDIUM risk
    elif len(warning_events) > 0 or len(caution_events) >= 2:
        risk_level = "MEDIUM"
        for w in warning_events:
            alerts.append(w["reason"])
        for ca in caution_events:
            alerts.append(ca["reason"])

    # LOW risk
    else:
        risk_level = "LOW"
        if short_tracks and not conflict_events:
            alerts.append(
                f"Not enough track history to estimate direction or speed for {short_tracks} object(s)."
            )
        elif not pedestrians_count or not vehicles_count:
            alerts.append("No pedestrian-vehicle pair was available to compare.")
        else:
            alerts.append("No pedestrian-vehicle conflict detected.")

    if short_tracks and conflict_events:
        alerts.append(
            f"{short_tracks} object(s) were ignored because they have fewer than 2 positions."
        )

    return risk_level, alerts


def _overall_risk(conflicts: list[dict[str, Any]]) -> str:
    levels = {item.get("risk_level") for item in conflicts}
    if "HIGH" in levels:
        return "HIGH"
    if "MEDIUM" in levels:
        return "MEDIUM"
    return "LOW"


def _calculate_safety_score(conflicts: list[dict[str, Any]], short_tracks: int = 0) -> int:
    """Compute a 0-100 safety score for dashboard display."""
    if not conflicts:
        deduction = min(short_tracks * 2, 10)
        return max(0, 100 - deduction)

    critical_count = sum(1 for c in conflicts if c.get("severity") == "CRITICAL" or c.get("risk_level") == "HIGH")
    warning_count = sum(1 for c in conflicts if c.get("severity") == "WARNING" or c.get("risk_level") == "MEDIUM")

    score = 100 - (critical_count * 25) - (warning_count * 12) - min(short_tracks, 5)

    if critical_count > 0:
        score = min(score, 60)
    elif warning_count > 0:
        score = min(score, 85)

    return max(0, min(100, score))


def _empty_result(reason: str, total_records: int = 0, duration: float = 0.0) -> dict[str, Any]:
    return {
        "pedestrians_detected": 0,
        "vehicles_detected": 0,
        "conflicts_detected": 0,
        "risk_level": "LOW",
        "safety_score": 100,
        "alerts": [reason],
        "conflicts": [],
        "conflict_details": [],
        "summary": {
            "total_records": total_records,
            "duration_seconds": duration,
            "critical_conflicts": 0,
            "warning_conflicts": 0,
            "caution_conflicts": 0,
        },
    }


def analyse_track_file(path: str | Path) -> dict[str, Any]:
    """Load a JSON track file and return the same result as analyse_tracks."""
    file_path = Path(path)
    with file_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    return analyse_tracks(payload)


def analyse_video(video_path: str | Path, **kwargs) -> dict[str, Any]:
    """Run Member 3's process_video, then score the tracks."""
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
