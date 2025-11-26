import os
import math
import matplotlib.pyplot as plt
from datetime import datetime

def fetch_and_group_data(user_id, mode_text, posture_text, db, start_date, end_date):
    mode_map = {"PRACTICE": 0, "EASY": 1, "HARD": 2}
    mode = mode_map.get(mode_text.upper(), 0)

    pose_name_map = {
        "Bridge Pose": 9,
        "Chair Pose": 6,
        "Downward-Facing Dog": 0,
        "Locust Pose": 7,
        "Plank Pose": 4,
        "Staff Pose": 5,
        "Triangle Pose": 8,
        "Warrior 1 Pose": 1,
        "Warrior 2 Pose": 2,
        "Warrior 3 Pose": 3
    }
    posture_id = pose_name_map.get(posture_text, None)
    if posture_id is None:
        return []

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    try:
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, timestamp, accuracy, mode, posture_id, user_id, session_id, countdown, `count`
                FROM record_picture
                WHERE user_id = %s
                AND mode = %s
                AND posture_id = %s
                AND timestamp BETWEEN %s AND %s
                ORDER BY `count`, timestamp ASC
                """,
                (user_id, mode, posture_id, start_dt, end_dt)
            )
            rows = cursor.fetchall()
    except Exception:
        return []

    if not rows:
        return []

    merged_rows = {}
    for r in rows:
        key = (r["count"], r["countdown"], r["timestamp"])
        if key not in merged_rows:
            merged_rows[key] = {"sum": r["accuracy"], "cnt": 1, "row": r}
        else:
            merged_rows[key]["sum"] += r["accuracy"]
            merged_rows[key]["cnt"] += 1
    combined = []
    for key, v in merged_rows.items():
        avg_acc = v["sum"] / v["cnt"]
        sample = v["row"].copy()
        sample["accuracy"] = avg_acc
        combined.append(sample)

    major_groups = {}
    for row in combined:
        major_groups.setdefault(row["count"], []).append(row)

    final_groups = []
    for major_key, rows_in_group in major_groups.items():
        rows_in_group.sort(key=lambda r: r["timestamp"] or datetime.min)  # sort by time
        cycles = []
        current_cycle = []
        prev_cd = None
        for r in rows_in_group:
            if r.get("countdown") is None:
                continue
            try:
                cd = int(r["countdown"])
            except Exception:
                continue

            if prev_cd is None:
                current_cycle = [r]
            else:
                if cd > prev_cd:  # new cycle
                    if current_cycle:
                        cycles.append(current_cycle)
                    current_cycle = [r]
                else:
                    current_cycle.append(r)
            prev_cd = cd
        if current_cycle:
            cycles.append(current_cycle)

        for idx, cycle in enumerate(cycles, start=1):
            obs_map = {}
            time_map = {}
            for rr in cycle:
                try:
                    k = int(rr["countdown"])
                except Exception:
                    continue
                if k not in obs_map:
                    obs_map[k] = float(rr["accuracy"])
                    time_map[k] = rr.get("timestamp")

            if not obs_map:
                continue

            cd_max = max(obs_map.keys())
            cd_min = min(obs_map.keys())

            filled_rows = []
            last_acc = None
            last_time = None
            for cd in range(cd_max, cd_min - 1, -1):
                if cd in obs_map:
                    last_acc = obs_map[cd]
                    last_time = time_map.get(cd, last_time)
                    fake_row = cycle[0].copy()
                    fake_row["countdown"] = cd
                    fake_row["accuracy"] = last_acc
                    fake_row["timestamp"] = last_time
                    filled_rows.append(fake_row)
                else:
                    if last_acc is not None:
                        fake_row = cycle[0].copy()
                        fake_row["countdown"] = cd
                        fake_row["accuracy"] = last_acc
                        fake_row["timestamp"] = last_time
                        filled_rows.append(fake_row)

            final_groups.append({
                "major": major_key,
                "minor": idx,
                "rows": filled_rows
            })

    return final_groups

def save_group_charts(groups, user_id, posture_text, mode_text):
    output_dir = os.path.join(os.path.dirname(__file__), "record_pic")
    os.makedirs(output_dir, exist_ok=True)
    paths = []

    for g in groups:
        major, minor, rows = g["major"], g["minor"], g["rows"]
        rows.sort(key=lambda r: r["countdown"], reverse=True)

        page_size = 21
        num_pages = math.ceil(len(rows) / page_size)
        num_pages = min(num_pages, 3)

        for page in range(num_pages):
            chunk = rows[page * page_size:(page + 1) * page_size]
            if not chunk:
                continue

            x_vals = [int(r["countdown"]) for r in chunk]
            y_vals = [float(r["accuracy"]) for r in chunk]
            times = [r["timestamp"] for r in chunk]

            times_sorted = sorted(times)
            t_start = times_sorted[0].strftime("%Y/%m/%d %H:%M:%S")
            t_end = times_sorted[-1].strftime("%Y/%m/%d %H:%M:%S")

            title_main = f"{mode_text.upper()}-{posture_text} ({major}-{minor}-{page + 1})"
            title_sub = f"{t_start} - {t_end}"

            plt.figure(figsize=(8, 5))
            plt.plot(x_vals, y_vals, marker="o", color="blue")

            for x, y in zip(x_vals, y_vals):
                plt.text(x, y + 1, f"{y:.0f}", ha="center", va="bottom", fontsize=8, color="black")

            plt.xlabel("Countdown (seconds)")
            plt.ylabel("Accuracy (%)")
            plt.ylim(0, 100)
            plt.xlim(max(x_vals), min(x_vals))
            plt.xticks(range(max(x_vals), min(x_vals) - 1, -2))

            plt.title(f"{title_main}\n{title_sub}", fontsize=14, fontweight="bold", loc="center", pad=15)
            plt.grid(True)
            plt.tight_layout()

            filename = f"{user_id}_{mode_text.upper()}_{posture_text.replace(' ', '_')}({major}-{minor}-{page + 1}).png"
            filepath = os.path.join(output_dir, filename)
            plt.savefig(filepath, dpi=150)
            plt.close()
            paths.append(filepath)

    return paths
