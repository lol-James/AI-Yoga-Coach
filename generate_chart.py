import os
import math
import matplotlib.pyplot as plt
from datetime import datetime


def fetch_and_group_data(user_id, mode_text, posture_text, db, start_date, end_date):
    """
    Fetch data from DB and group it properly.
    Fix 2 issues:
      1. Merge same timestamp/countdown rows (average score)
      2. Fill missing countdown seconds with same score
    """
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
        print(f"[DEBUG] Invalid posture_text: {posture_text}")
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
    except Exception as e:
        print("fetch_and_group_data DB error:", e)
        return []

    if not rows:
        print("[DEBUG] No data found in DB for this filter.")
        return []

    # --- (1) Merge duplicate timestamp/countdown entries ---
    merged_rows = {}
    for r in rows:
        key = (r["count"], r["countdown"])
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

    # --- (2) Fill missing countdowns with last known score ---
    # Group by 'count'
    major_groups = {}
    for row in combined:
        major_groups.setdefault(row["count"], []).append(row)

    final_groups = []
    for major_key, rows_in_group in major_groups.items():
        rows_in_group.sort(key=lambda r: r["countdown"], reverse=True)

        # Find max and min countdown in this group
        cds = [int(r["countdown"]) for r in rows_in_group if r["countdown"] is not None]
        if not cds:
            continue
        cd_max, cd_min = max(cds), min(cds)

        # Fill missing countdowns (use last known accuracy)
        cd_map = {int(r["countdown"]): float(r["accuracy"]) for r in rows_in_group}
        filled_rows = []
        last_acc = None
        for cd in range(cd_max, cd_min - 1, -1):
            acc = cd_map.get(cd, last_acc)
            if acc is not None:
                fake_row = rows_in_group[0].copy()
                fake_row["countdown"] = cd
                fake_row["accuracy"] = acc
                filled_rows.append(fake_row)
            if cd in cd_map:
                last_acc = cd_map[cd]

        # Split into minor groups (countdown reset pattern)
        sub_groups, temp = [], []
        prev_cd = None
        for r in filled_rows:
            cd = int(r["countdown"])
            if prev_cd is not None and cd > prev_cd:
                sub_groups.append(temp)
                temp = []
            temp.append(r)
            prev_cd = cd
        if temp:
            sub_groups.append(temp)

        for idx, sg in enumerate(sub_groups, start=1):
            final_groups.append({
                "major": major_key,
                "minor": idx,
                "rows": sg
            })

    print(f"[DEBUG] Found {len(final_groups)} groups after fill.")
    return final_groups


def save_group_charts(groups, user_id, posture_text, mode_text):
    """
    Draw and save charts for each group.
    X-axis: countdown (decreasing), 21 points per page, up to 3 pages.
    """
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

            t_start = times[0].strftime("%Y:%m:%d:%H:%M:%S")
            t_end = times[-1].strftime("%Y:%m:%d:%H:%M:%S")

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
