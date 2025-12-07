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
    """
    Iterates through data groups and distributes data evenly across charts.
    - Count <= 21: 1 chart
    - Count 22-42: 2 charts (split evenly)
    - Count > 42: 3+ charts (split evenly)
    
    Saves files to 'record_pic' folder with format: 
    {user_id}_{mode}_{posture}_{major}-{minor}-{page}.png
    """
    if not groups:
        return []

    # Ensure output directory exists
    output_dir = os.path.join(os.path.dirname(__file__), "record_pic")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    chart_paths = []
    base_capacity = 21  # Max points per chart if only 1 page

    # Sanitize names for filename
    safe_posture = posture_text.replace(" ", "_").replace("/", "-")
    safe_mode = mode_text.upper()

    # --- Outer Loop: Process each group (session/cycle) ---
    for g in groups:
        # Extract data from the group dictionary
        # The dictionary structure comes from fetch_and_group_data
        major = g.get("major", 0)
        minor = g.get("minor", 0)
        rows = g.get("rows", [])
        
        if not rows:
            continue

        # Sort rows by countdown descending (start from max countdown)
        # rows.sort(key=lambda r: r["countdown"], reverse=True) # Optional: depends on if you want time order or countdown order

        total_count = len(rows)

        # Calculate required pages (ceiling division)
        if total_count == 0:
            num_pages = 0
        else:
            num_pages = (total_count + base_capacity - 1) // base_capacity

        current_idx = 0

        # --- Inner Loop: Generate pages for this group ---
        for page in range(num_pages):
            # --- Dynamic Distribution Logic ---
            items_remaining = total_count - current_idx
            pages_remaining = num_pages - page
            
            # Calculate chunk size for this page
            chunk_size = (items_remaining + pages_remaining - 1) // pages_remaining
            
            # Slice data for current page
            end_idx = current_idx + chunk_size
            chunk = rows[current_idx : end_idx]
            current_idx = end_idx

            if not chunk:
                continue

            # Prepare plotting data
            try:
                x_vals = [int(r["countdown"]) for r in chunk]
                y_vals = [float(r["accuracy"]) for r in chunk]
                times = [r["timestamp"] for r in chunk]
            except KeyError as e:
                print(f"Data error in group {major}-{minor}: {e}")
                continue

            # Determine time range for title
            # Filter out None timestamps just in case
            valid_times = [t for t in times if t is not None]
            if valid_times:
                times_sorted = sorted(valid_times)
                t_start = times_sorted[0].strftime("%Y/%m/%d %H:%M:%S")
                t_end = times_sorted[-1].strftime("%Y/%m/%d %H:%M:%S")
            else:
                t_start = "N/A"
                t_end = "N/A"

            # Title format: MODE-POSTURE (Major-Minor-Page)
            # page + 1 makes it 1-based index
            title_main = f"{safe_mode}-{posture_text} ({major}-{minor}-{page + 1})"
            title_sub = f"{t_start} - {t_end}"

            # Setup plot
            plt.figure(figsize=(8, 5))
            plt.plot(x_vals, y_vals, marker="o", color="blue")

            # Add value labels
            for x, y in zip(x_vals, y_vals):
                plt.text(x, y + 1, f"{y:.0f}", ha="center", va="bottom", fontsize=8, color="black")

            plt.xlabel("Countdown (seconds)")
            plt.ylabel("Accuracy (%)")
            plt.ylim(0, 100)
            
            # Standard scaling: fit to data range
            if len(x_vals) > 0:
                x_max = max(x_vals)
                x_min = min(x_vals)
                if x_max == x_min:
                    # Handle single point case
                    plt.xlim(x_max + 1, x_max - 1)
                    plt.xticks([x_max])
                else:
                    plt.xlim(x_max, x_min)
                    plt.xticks(range(x_max, x_min - 1, -2))

            plt.title(f"{title_main}\n{title_sub}", fontsize=14, fontweight="bold", loc="center", pad=15)
            plt.figtext(0.99, 0.995, "ID Format: Login Times - Complete Count - Page", 
            ha='right', va='top', 
            fontsize=9, color='#555555')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()

            # Save chart
            # Filename includes major/minor to prevent overwriting
            filename = f"{user_id}_{safe_mode}_{safe_posture}_{major}-{minor}-{page + 1}.png"
            save_path = os.path.join(output_dir, filename)
            
            plt.savefig(save_path)
            plt.close()

            chart_paths.append(save_path)

    return chart_paths