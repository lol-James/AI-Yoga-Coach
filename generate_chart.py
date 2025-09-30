import math
import os
from datetime import datetime, time as dtime
import matplotlib.pyplot as plt
from collections import defaultdict

def _round_half_up(value):
    """Round to nearest integer (half-up)."""
    return int(math.floor(value + 0.5))

# Posture and mode mappings (consistent with main.py)
_POSTURE_MAP = {
    "Bridge Pose": 0,
    "Chair Pose": 1,
    "Downward Facing Dog": 2,
    "Locust Pose": 3,
    "Plank Pose": 4,
    "Staff Pose": 5,
    "Triangle Pose": 6,
    "Warrior 1": 7,
    "Warrior 2": 8,
    "Warrior 3": 9,
}

_MODE_MAP = {"PRACTICE": 0, "EASY": 1, "HARD": 2}

def _format_label(dt_obj, total_days):
    """Format x-axis label based on total time span."""
    if total_days >= 365:
        return f"{dt_obj.year}"
    if total_days >= 31:
        return dt_obj.strftime("%Y-%m")
    if total_days >= 1:
        return dt_obj.strftime("%m-%d")
    return dt_obj.strftime("%H:%M")

def generate_chart(user_id, mode_text, posture_text, start_date, end_date, db, output_dir=None):
    """
    Generate a chart averaged into 15 segments.
    - user_id: int
    - mode_text: "Practice"/"Easy"/"Hard"
    - posture_text: posture name (e.g. "Bridge Pose")
    - start_date, end_date: Python date objects
    - db: pymysql connection
    - output_dir: optional, where to save image
    Returns the image path, or None if no data found.
    """
    if not user_id:
        raise ValueError("user_id required")

    mode_val = _MODE_MAP.get(str(mode_text).upper(), 0)
    posture_id = _POSTURE_MAP.get(posture_text, None)

    start_dt = datetime.combine(start_date, dtime.min)
    end_dt = datetime.combine(end_date, dtime.max)

    try:
        with db.cursor() as cursor:
            if posture_id is None:
                cursor.execute(
                    "SELECT timestamp, accuracy FROM record_picture "
                    "WHERE user_id=%s AND mode=%s AND timestamp BETWEEN %s AND %s "
                    "ORDER BY timestamp",
                    (int(user_id), int(mode_val), start_dt, end_dt)
                )
            else:
                cursor.execute(
                    "SELECT timestamp, accuracy FROM record_picture "
                    "WHERE user_id=%s AND mode=%s AND posture_id=%s AND timestamp BETWEEN %s AND %s "
                    "ORDER BY timestamp",
                    (int(user_id), int(mode_val), int(posture_id), start_dt, end_dt)
                )
            rows = cursor.fetchall()
    except Exception:
        rows = []

    if not rows:
        return None

    # Adjust actual range to cover only the first to last data timestamp
    all_ts = []
    for r in rows:
        ts = r.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except Exception:
                continue
        if ts:
            all_ts.append(ts)

    if not all_ts:
        return None

    actual_start = min(all_ts)
    actual_end = max(all_ts)

    # Fallback if range is invalid (e.g., same timestamp)
    if actual_start >= actual_end:
        actual_start = start_dt
        actual_end = end_dt

    SEGMENTS = 15
    total_seconds = max(1.0, (actual_end - actual_start).total_seconds())
    sums = [0.0] * SEGMENTS
    counts = [0] * SEGMENTS

    for r in rows:
        ts = r.get("timestamp")
        acc = r.get("accuracy")
        if ts is None or acc is None:
            continue
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except Exception:
                continue
        if ts < actual_start or ts > actual_end:
            continue
        sec = (ts - actual_start).total_seconds()
        frac = sec / total_seconds
        idx = int(frac * SEGMENTS)
        if idx >= SEGMENTS:
            idx = SEGMENTS - 1
        sums[idx] += float(acc)
        counts[idx] += 1

    y_values = []
    for i in range(SEGMENTS):
        if counts[i] > 0:
            avg = sums[i] / counts[i]
            y_values.append(float(_round_half_up(avg)))
        else:
            y_values.append(float("nan"))

    segment_starts = [actual_start + (actual_end - actual_start) * (i / SEGMENTS) for i in range(SEGMENTS)]
    total_days = (actual_end - actual_start).total_seconds() / 86400.0
    x_labels = [_format_label(s, total_days) for s in segment_starts]

    if total_days >= 365:
        x_unit = "Year"
    elif total_days >= 31:
        x_unit = "Month"
    elif total_days >= 1:
        x_unit = "Day"
    else:
        x_unit = "Time"

    fig, ax = plt.subplots(figsize=(10, 5))
    x_positions = list(range(SEGMENTS))
    ax.plot(x_positions, y_values, marker="o", linestyle="-", linewidth=1)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels, rotation=45, ha="right")
    ax.set_xlim(-0.5, SEGMENTS - 0.5)
    ax.set_xlabel(f"Time ({x_unit})")
    ax.set_title(f"{posture_text} - {mode_text}")

    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticks(list(range(0, 101, 5)), minor=True)
    ax.grid(which="major", linestyle="solid", linewidth=0.6, alpha=0.6)
    ax.grid(which="minor", linestyle=":", linewidth=0.5, alpha=0.4)

    for i, y in enumerate(y_values):
        if not math.isnan(y):
            ax.hlines(y, xmin=0, xmax=i, linestyles="dashed", linewidth=0.7, alpha=0.7)

    for i, y in enumerate(y_values):
        if not math.isnan(y):
            ax.annotate(str(int(y)), (i, y), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8)

    plt.tight_layout()

    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "record_pic")
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{user_id}.png")
    plt.savefig(out_path)
    plt.close(fig)
    return out_path

def fetch_and_group_data(user_id, mode_text, posture_text, db):
    """Fetch data from DB, merge same-second records, and split into groups by time continuity."""
    mode_val = _MODE_MAP.get(str(mode_text).upper(), 0)
    posture_id = _POSTURE_MAP.get(posture_text, None)

    query = (
        "SELECT timestamp, accuracy FROM record_picture "
        "WHERE user_id=%s AND mode=%s "
        + ("AND posture_id=%s " if posture_id is not None else "")
        + "ORDER BY timestamp"
    )
    params = (user_id, mode_val) if posture_id is None else (user_id, mode_val, posture_id)

    try:
        with db.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
    except Exception:
        rows = []

    if not rows:
        return []

    # Step 1: merge same-second data
    merged = defaultdict(list)
    for r in rows:
        ts = r.get("timestamp")
        acc = r.get("accuracy")
        if ts is None or acc is None:
            continue
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except Exception:
                continue
        key = ts.replace(microsecond=0)
        merged[key].append(float(acc))

    merged_data = []
    for ts, vals in merged.items():
        avg = sum(vals) / len(vals)
        merged_data.append((ts, int(round(avg))))

    merged_data.sort(key=lambda x: x[0])

    # Step 2: split into groups by continuity
    groups = []
    current_group = []
    prev_ts = None
    for ts, acc in merged_data:
        if prev_ts is None:
            current_group.append((ts, acc))
        else:
            delta = (ts - prev_ts).total_seconds()
            if delta == 1:  # continuous second
                current_group.append((ts, acc))
            else:  # break
                groups.append(current_group)
                current_group = [(ts, acc)]
        prev_ts = ts
    if current_group:
        groups.append(current_group)

    return groups

def save_group_charts(groups, user_id, posture_text, mode_text, output_dir=None):
    """Save one chart per group with time range subtitle."""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "record_pic")
    os.makedirs(output_dir, exist_ok=True)

    paths = []
    for idx, group in enumerate(groups):
        times = list(range(1, len(group) + 1))
        scores = [acc for _, acc in group]

        start_time = group[0][0]
        end_time = group[-1][0]
        time_range = f"{start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')}"

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(times, scores, marker="o", linestyle="-", linewidth=1)

        ax.set_title(f"{posture_text} - {mode_text} (Group {idx+1})")
        plt.suptitle(time_range, fontsize=9, y=0.98)

        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Score")
        ax.set_ylim(0, 105)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_yticks(list(range(0, 101, 5)), minor=True)
        ax.grid(which="major", linestyle="solid", linewidth=0.6, alpha=0.6)
        ax.grid(which="minor", linestyle=":", linewidth=0.5, alpha=0.4)

        for i, y in enumerate(scores):
            ax.annotate(str(int(y)), (times[i], y),
                        textcoords="offset points", xytext=(0, 6),
                        ha="center", fontsize=8)

        plt.tight_layout()
        path = os.path.join(output_dir, f"{user_id}_group{idx+1}.png")
        plt.savefig(path)
        plt.close(fig)
        paths.append(path)
    return paths

def get_chart_path(user_id, group_index, total_groups, output_dir=None):
    """Return the file path of the chart for the given group index (1-based)."""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "record_pic")
    return os.path.join(output_dir, f"{user_id}_group{group_index}.png")
