# complete replacement for record_logger.py
from PyQt5.QtCore import QTimer
from datetime import datetime, timedelta

class RecordLogger:
    """
    Logger that:
      - writes per-second samples into record_picture
      - tracks login/logout sessions in a new table `record_session`
      - updates record_detail (completion count + max/min accuracy + usage stats)
      - provides load_statistics(mode) for the progress page
      - consolidates duplicate rows and ensures initial rows exist per user/mode
    """
    def __init__(self, ui, db, user_id=None):
        self.ui = ui
        self.db = db
        self.user_id = user_id
        self._session_start_time = None
        self._current_session_id = None
        self._current_session_mode = None

        # Pose order must match statistics_treewidget order (index 0..9)
        self.pose_names = [
            "Bridge Pose", "Chair Pose", "Downward Facing Dog",
            "Locust Pose", "Plank Pose", "Staff Pose",
            "Triangle Pose", "Warrior 1", "Warrior 2", "Warrior 3"
        ]

        # Alias map (normalize names)
        self.pose_name_alias = {
            "Bridge_Pose": "Bridge Pose", "Bridge Pose": "Bridge Pose",
            "Chair_Pose": "Chair Pose", "Chair Pose": "Chair Pose",
            "Downward-Facing_Dog": "Downward Facing Dog", "Downward Facing Dog": "Downward Facing Dog",
            "Locust_Pose": "Locust Pose", "Locust Pose": "Locust Pose",
            "Plank_Pose": "Plank Pose", "Plank Pose": "Plank Pose",
            "Staff_Pose": "Staff Pose", "Staff Pose": "Staff Pose",
            "Triangle_Pose": "Triangle Pose", "Triangle Pose": "Triangle Pose",
            "Warrior_I": "Warrior 1", "Warrior 1": "Warrior 1",
            "Warrior_II": "Warrior 2", "Warrior 2": "Warrior 2",
            "Warrior_III": "Warrior 3", "Warrior 3": "Warrior 3",
        }

        # UI label mapping (for progress page)
        self.pose_labels = {
            "Bridge Pose": (self.ui.label_33, self.ui.label_54, self.ui.label_53),
            "Chair Pose": (self.ui.label_55, self.ui.label_56, self.ui.label_35),
            "Downward Facing Dog": (self.ui.label_37, self.ui.label_58, self.ui.label_57),
            "Locust Pose": (self.ui.label_59, self.ui.label_60, self.ui.label_39),
            "Plank Pose": (self.ui.label_61, self.ui.label_62, self.ui.label_41),
            "Staff Pose": (self.ui.label_63, self.ui.label_43, self.ui.label_64),
            "Triangle Pose": (self.ui.label_65, self.ui.label_66, self.ui.label_45),
            "Warrior 1": (self.ui.label_67, self.ui.label_68, self.ui.label_47),
            "Warrior 2": (self.ui.label_69, self.ui.label_70, self.ui.label_49),
            "Warrior 3": (self.ui.label_71, self.ui.label_72, self.ui.label_51)
        }

        self._monitor_timer = QTimer()
        self._monitor_timer.timeout.connect(lambda: None)

    # --- user id management --------------------------------
    def set_user_id(self, user_id):
        """
        Called when Account emits user_id (login or logout).
        This sets internal user_id, consolidates records, and ensures rows.
        It does NOT automatically start/stop a session.
        """
        try:
            self.user_id = int(user_id) if user_id not in (None, "", 0) else None
        except Exception:
            self.user_id = None
            return
        if self.user_id:
            self.consolidate_duplicate_records()
            for m in (0, 1, 2):
                self.ensure_user_records(mode_int=m)

    # --- session tracking methods -------------------------
    def start_session(self, mode=None):
        """
        Start a new session.
        Before inserting, close any previous open sessions for this user.
        """
        if not self.user_id:
            return
        try:
            now = datetime.now()
            self._session_start_time = now
            self._current_session_id = str(now.timestamp())
            self._current_session_mode = self._mode_to_int(mode)
            with self.db.cursor() as cursor:
                cursor.execute(
                    "UPDATE record_session SET end_time=%s WHERE user_id=%s AND end_time IS NULL",
                    (now, self.user_id)
                )
                cursor.execute(
                    "INSERT INTO record_session (user_id, session_id, start_time, end_time, mode) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (self.user_id, self._current_session_id, now, None, self._current_session_mode)
                )
            self.db.commit()
        except Exception:
            pass

    def end_session(self, end_time=None):
        """
        End the current session.
        Update the row matching current session_id if possible,
        otherwise update the most recent NULL-end row for this user.
        """
        if not self.user_id and not self._current_session_id:
            return
        try:
            et = end_time if end_time is not None else datetime.now()
            with self.db.cursor() as cursor:
                if self._current_session_id:
                    cursor.execute(
                        "UPDATE record_session SET end_time=%s WHERE user_id=%s AND session_id=%s",
                        (et, self.user_id, self._current_session_id)
                    )
                    if getattr(cursor, "rowcount", None) == 0:
                        cursor.execute(
                            "UPDATE record_session SET end_time=%s WHERE user_id=%s AND end_time IS NULL "
                            "ORDER BY start_time DESC LIMIT 1",
                            (et, self.user_id)
                        )
                else:
                    cursor.execute(
                        "UPDATE record_session SET end_time=%s WHERE user_id=%s AND end_time IS NULL "
                        "ORDER BY start_time DESC LIMIT 1",
                        (et, self.user_id)
                    )
            self.db.commit()
        finally:
            self._session_start_time = None
            self._current_session_id = None
            self._current_session_mode = None

    # --- write per-second sample (record_picture) ---
    def add_picture_record(self, posture_id, posture_name, accuracy, mode):
        if not self.user_id:
            return
        mode_int = self._mode_to_int(mode)
        if not self._current_session_id:
            self._session_start_time = datetime.now()
            self._current_session_id = str(self._session_start_time.timestamp())
            self._current_session_mode = mode_int
            try:
                with self.db.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO record_session (user_id, session_id, start_time, end_time, mode) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (self.user_id, self._current_session_id, self._session_start_time, None, self._current_session_mode)
                    )
                self.db.commit()
            except Exception:
                pass

        session_id = self._current_session_id
        ts = datetime.now()
        canonical_id, cname = self._get_canonical_id(posture_id, posture_name)
        if canonical_id is None:
            return
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO record_picture (timestamp, accuracy, mode, posture_id, user_id, session_id) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (ts, float(accuracy), mode_int, canonical_id, int(self.user_id), session_id)
                )
            self.db.commit()
        except Exception:
            pass

    # --- update record_detail in real time ---
    def increment_pose_count(self, posture_id, posture_name, mode, accuracy=None, delta=1):
        if not self.user_id or delta <= 0:
            return
        try:
            mode_int = self._mode_to_int(mode)
            cname = self.pose_name_alias.get(posture_name, posture_name)
            if cname not in self.pose_names:
                return
            canonical_id = self.pose_names.index(cname)
            with self.db.cursor() as cursor:
                cursor.execute(
                    "SELECT id, max_accuracy, min_accuracy, total_completed "
                    "FROM record_detail WHERE user_id=%s AND posture_id=%s AND mode=%s LIMIT 1",
                    (self.user_id, canonical_id, mode_int)
                )
                existing = cursor.fetchone()
                if existing:
                    new_total = (existing.get("total_completed") or 0) + int(delta)
                    max_acc = existing.get("max_accuracy")
                    min_acc = existing.get("min_accuracy")
                    if accuracy is not None:
                        if max_acc is None or accuracy > max_acc:
                            max_acc = accuracy
                        if min_acc is None or accuracy < min_acc:
                            min_acc = accuracy
                    cursor.execute(
                        "UPDATE record_detail SET total_completed=%s, max_accuracy=%s, min_accuracy=%s "
                        "WHERE id=%s",
                        (new_total, max_acc, min_acc, existing.get("id"))
                    )
                else:
                    cursor.execute(
                        "INSERT INTO record_detail "
                        "(user_id, mode, total_posture_count, daily_max_app_opens, max_daily_usage_hours, "
                        "min_daily_usage_hours, longest_streak_days, posture_id, posture_name, total_completed, "
                        "max_accuracy, min_accuracy) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (self.user_id, mode_int, 0, 0, 0.0, 0.0, 0,
                         canonical_id, cname, int(delta),
                         float(accuracy) if accuracy is not None else None,
                         float(accuracy) if accuracy is not None else None)
                    )
                cursor.execute(
                    "SELECT SUM(total_completed) AS s FROM record_detail WHERE user_id=%s AND mode=%s",
                    (self.user_id, mode_int)
                )
                srow = cursor.fetchone()
                total_sum = int(srow.get("s") or 0) if srow else 0
                cursor.execute(
                    "UPDATE record_detail SET total_posture_count=%s WHERE user_id=%s AND mode=%s",
                    (total_sum, self.user_id, mode_int)
                )
            self.db.commit()
        except Exception:
            pass

    def update_pose_accuracy(self, posture_id=None, posture_name=None, mode=None, accuracy=None):
        if not self.user_id or accuracy is None:
            return
        try:
            mode_int = self._mode_to_int(mode)
            canonical_id, cname = self._get_canonical_id(posture_id, posture_name)
            if canonical_id is None:
                return
            with self.db.cursor() as cursor:
                cursor.execute(
                    "SELECT id, max_accuracy, min_accuracy FROM record_detail "
                    "WHERE user_id=%s AND posture_id=%s AND mode=%s LIMIT 1",
                    (self.user_id, canonical_id, mode_int)
                )
                existing = cursor.fetchone()
                if existing:
                    max_acc = existing.get("max_accuracy")
                    min_acc = existing.get("min_accuracy")
                    if max_acc is None or accuracy > max_acc:
                        max_acc = accuracy
                    if min_acc is None or accuracy < min_acc:
                        min_acc = accuracy
                    cursor.execute(
                        "UPDATE record_detail SET max_accuracy=%s, min_accuracy=%s WHERE id=%s",
                        (max_acc, min_acc, existing.get("id"))
                    )
                else:
                    cursor.execute(
                        "INSERT INTO record_detail (user_id, mode, total_posture_count, daily_max_app_opens, "
                        "max_daily_usage_hours, min_daily_usage_hours, longest_streak_days, posture_id, posture_name, "
                        "total_completed, max_accuracy, min_accuracy) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (self.user_id, mode_int, 0, 0, 0.0, 0.0, 0,
                         canonical_id, cname, 0, float(accuracy), float(accuracy))
                    )
            self.db.commit()
        except Exception:
            pass

    # --- sync aggregated detail from the UI treewidget ----
    def update_detail_from_tree(self, mode):
        if not self.user_id:
            return
        mode_int = self._mode_to_int(mode)
        counts = {}
        for idx, pname in enumerate(self.pose_names):
            cnt = 0
            try:
                item = self.ui.statistics_treewidget.topLevelItem(idx)
                if item:
                    txt = item.text(1)
                    cnt = int(txt) if txt and txt.isdigit() else 0
            except Exception:
                cnt = 0
            counts[pname] = cnt
        total_count = sum(counts.values())
        usage = self.calculate_usage_stats(mode_int)
        total_usage_hours = round(float(usage.get("total_usage_hours", 0.0) or 0.0), 4)
        try:
            with self.db.cursor() as cursor:
                for idx, pname in enumerate(self.pose_names):
                    cnt = counts.get(pname, 0)
                    cursor.execute(
                        "SELECT MAX(accuracy) AS max_acc, MIN(accuracy) AS min_acc "
                        "FROM record_picture WHERE user_id=%s AND mode=%s AND posture_id=%s",
                        (self.user_id, mode_int, idx)
                    )
                    acc_row = cursor.fetchone()
                    max_acc = acc_row.get("max_acc") if acc_row else None
                    min_acc = acc_row.get("min_acc") if acc_row else None
                    cursor.execute(
                        "SELECT id FROM record_detail WHERE user_id=%s AND posture_id=%s AND mode=%s LIMIT 1",
                        (self.user_id, idx, mode_int)
                    )
                    existing = cursor.fetchone()
                    if existing:
                        cursor.execute(
                            "UPDATE record_detail SET "
                            "total_posture_count=%s, daily_max_app_opens=%s, "
                            "max_daily_usage_hours=%s, min_daily_usage_hours=%s, "
                            "longest_streak_days=%s, total_usage_hours=%s, "
                            "posture_name=%s, total_completed=%s, max_accuracy=%s, min_accuracy=%s "
                            "WHERE id=%s",
                            (total_count,
                             usage.get("daily_max_app_opens", 0),
                             usage.get("max_daily_usage_hours", 0.0),
                             usage.get("min_daily_usage_hours", 0.0),
                             usage.get("longest_streak_days", 0),
                             total_usage_hours,
                             pname,
                             cnt,
                             max_acc, min_acc,
                             existing.get("id"))
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO record_detail (user_id, mode, total_posture_count, daily_max_app_opens, "
                            "max_daily_usage_hours, min_daily_usage_hours, longest_streak_days, total_usage_hours, "
                            "posture_id, posture_name, total_completed, max_accuracy, min_accuracy) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (self.user_id, mode_int, total_count,
                             usage.get("daily_max_app_opens", 0),
                             usage.get("max_daily_usage_hours", 0.0),
                             usage.get("min_daily_usage_hours", 0.0),
                             usage.get("longest_streak_days", 0),
                             total_usage_hours,
                             idx, pname, cnt,
                             max_acc, min_acc)
                        )
            self.db.commit()
        except Exception:
            pass

    # --- load statistics for progress page -----------------
    def load_statistics(self, mode):
        result = {
            "counts": {p: 0 for p in self.pose_names},
            "per_pose_accuracy": {p: {"max": None, "min": None} for p in self.pose_names},
            "total_count": 0,
            "max_pose": (None, 0),
            "min_pose": (None, 0),
            "usage": {
                "total_days": 0,
                "total_usage_hours": 0.0,
                "daily_max_app_opens": 0,
                "max_daily_usage_hours": 0.0,
                "min_daily_usage_hours": 0.0,
                "longest_streak_days": 0
            }
        }
        if not self.user_id:
            return result
        mode_int = self._mode_to_int(mode)
        try:
            with self.db.cursor() as cursor:
                if mode_int is None:
                    cursor.execute(
                        "SELECT posture_id, posture_name, SUM(total_completed) AS total_completed, "
                        "MAX(max_accuracy) AS max_accuracy, MIN(min_accuracy) AS min_accuracy "
                        "FROM record_detail WHERE user_id=%s GROUP BY posture_id, posture_name",
                        (self.user_id,)
                    )
                else:
                    cursor.execute(
                        "SELECT posture_id, posture_name, total_completed, max_accuracy, min_accuracy "
                        "FROM record_detail WHERE user_id=%s AND mode=%s",
                        (self.user_id, mode_int)
                    )
                rows = cursor.fetchall()
            for r in rows:
                raw_name = r.get("posture_name") or ""
                pname = self.pose_name_alias.get(raw_name, raw_name)
                if pname not in result["counts"]:
                    continue
                cnt = int(r.get("total_completed") or 0)
                max_acc = r.get("max_accuracy")
                min_acc = r.get("min_accuracy")
                result["counts"][pname] = cnt
                result["per_pose_accuracy"][pname] = {
                    "max": float(max_acc) if max_acc is not None else None,
                    "min": float(min_acc) if min_acc is not None else None
                }
            counts_list = [(p, result["counts"][p]) for p in self.pose_names]
            total = sum(cnt for _, cnt in counts_list)
            result["total_count"] = total
            if total > 0:
                result["max_pose"] = max(counts_list, key=lambda x: x[1])
                result["min_pose"] = min(counts_list, key=lambda x: x[1])
            else:
                result["max_pose"] = (self.pose_names[0], 0)
                result["min_pose"] = (self.pose_names[0], 0)
            usage = self.calculate_usage_stats(mode_int)
            result["usage"].update(usage)
        except Exception:
            pass
        return result

    # --- usage stats from record_session + record_picture -----
    def calculate_usage_stats(self, mode_int):
        """
        Usage stats across all modes.
        - total_days: number of distinct usage days
        - total_usage_hours: total hours of all sessions
        - daily_max_app_opens: max opens per day
        - max/min_daily_usage_hours: longest/shortest single session
        - longest_streak_days: longest streak of consecutive days
        """
        out = {
            "total_days": 0,
            "total_usage_hours": 0.0,
            "total_usage_days": 0.0,
            "daily_max_app_opens": 0,
            "max_daily_usage_hours": 0.0,
            "min_daily_usage_hours": 0.0,
            "longest_streak_days": 0
        }
        if not self.user_id:
            return out
        try:
            session_durations = []
            day_map = {}
            with self.db.cursor() as cursor:
                cursor.execute(
                    "SELECT rs.session_id, rs.start_time, rs.end_time "
                    "FROM record_session rs WHERE rs.user_id=%s ORDER BY rs.start_time",
                    (self.user_id,)
                )
                sess_rows = cursor.fetchall()
                for s in sess_rows:
                    st = s.get("start_time")
                    et = s.get("end_time") or datetime.now()
                    if isinstance(st, str):
                        st = datetime.fromisoformat(st)
                    if isinstance(et, str):
                        et = datetime.fromisoformat(et)
                    dur = max(0.0, (et - st).total_seconds() / 3600.0)
                    session_durations.append(dur)
                    day = st.date()
                    rec = day_map.setdefault(day, {"opens": 0})
                    rec["opens"] += 1
                cursor.execute(
                    "SELECT rp.session_id, MIN(rp.timestamp) AS st, MAX(rp.timestamp) AS et, DATE(rp.timestamp) AS day "
                    "FROM record_picture rp "
                    "LEFT JOIN record_session rs ON (rp.session_id=rs.session_id AND rp.user_id=rs.user_id) "
                    "WHERE rp.user_id=%s AND rs.session_id IS NULL "
                    "GROUP BY rp.session_id, day ORDER BY st",
                    (self.user_id,)
                )
                rows = cursor.fetchall()
                for r in rows:
                    st = r.get("st")
                    et = r.get("et") or st
                    if isinstance(st, str):
                        st = datetime.fromisoformat(st)
                    if isinstance(et, str):
                        et = datetime.fromisoformat(et)
                    dur = max(0.0, (et - st).total_seconds() / 3600.0)
                    session_durations.append(dur)
                    day = st.date()
                    rec = day_map.setdefault(day, {"opens": 0})
                    rec["opens"] += 1
            if not day_map and not session_durations:
                return out
            days_sorted = sorted(day_map.keys())
            total_hours = sum(session_durations)
            out["total_days"] = len(days_sorted)
            out["total_usage_hours"] = round(total_hours, 4)
            out["total_usage_days"] = round(total_hours / 24.0, 4)
            opens_list = [day_map[d]["opens"] for d in days_sorted] if day_map else []
            out["daily_max_app_opens"] = max(opens_list) if opens_list else 0
            if session_durations:
                out["max_daily_usage_hours"] = round(max(session_durations), 3)
                out["min_daily_usage_hours"] = round(min(session_durations), 3)
            longest = current = 1
            for i in range(1, len(days_sorted)):
                if (days_sorted[i] - days_sorted[i - 1]).days == 1:
                    current += 1
                    longest = max(longest, current)
                else:
                    current = 1
            out["longest_streak_days"] = longest if days_sorted else 0
        except Exception:
            pass
        return out

    # --- DB cleanup / ensure rows ---------------------------------
    def consolidate_duplicate_records(self, mode_int=None):
        """
        Merge duplicate record_detail rows for a user.
        Rows with the same normalized posture name are consolidated.
        """
        if not self.user_id:
            return
        try:
            with self.db.cursor() as cursor:
                if mode_int is None:
                    cursor.execute(
                        "SELECT id, mode, posture_id, posture_name, total_completed, max_accuracy, min_accuracy "
                        "FROM record_detail WHERE user_id=%s ORDER BY mode, id",
                        (self.user_id,)
                    )
                else:
                    cursor.execute(
                        "SELECT id, mode, posture_id, posture_name, total_completed, max_accuracy, min_accuracy "
                        "FROM record_detail WHERE user_id=%s AND mode=%s ORDER BY id",
                        (self.user_id, mode_int)
                    )
                rows = cursor.fetchall()
            groups = {}
            for r in rows:
                mode = r.get("mode")
                raw = r.get("posture_name") or ""
                normalized = self.pose_name_alias.get(raw, raw)
                key = (mode, normalized)
                groups.setdefault(key, []).append(r)
            with self.db.cursor() as cursor:
                for (mode, normalized), group in groups.items():
                    if len(group) <= 1:
                        continue
                    try:
                        canonical_id = self.pose_names.index(normalized) if normalized in self.pose_names else None
                    except ValueError:
                        canonical_id = None
                    sum_total = sum(int(g.get("total_completed") or 0) for g in group)
                    max_acc = None
                    min_acc = None
                    ids = []
                    for g in group:
                        ids.append(g.get("id"))
                        ma = g.get("max_accuracy")
                        mi = g.get("min_accuracy")
                        if ma is not None:
                            max_acc = ma if (max_acc is None or ma > max_acc) else max_acc
                        if mi is not None:
                            min_acc = mi if (min_acc is None or mi < min_acc) else min_acc
                    keep_id = min(ids)
                    cursor.execute(
                        "UPDATE record_detail SET posture_id=%s, posture_name=%s, total_completed=%s, max_accuracy=%s, min_accuracy=%s "
                        "WHERE id=%s",
                        (canonical_id if canonical_id is not None else group[0].get("posture_id"),
                         normalized, sum_total, max_acc, min_acc, keep_id)
                    )
                    delete_ids = [i for i in ids if i != keep_id]
                    if delete_ids:
                        placeholders = ",".join(["%s"] * len(delete_ids))
                        cursor.execute(
                            f"DELETE FROM record_detail WHERE id IN ({placeholders})",
                            tuple(delete_ids)
                        )
            self.db.commit()
        except Exception:
            pass

    def ensure_user_records(self, mode_int=None):
        """
        Ensure record_detail rows exist for each pose and mode.
        If mode_int is None, create rows for modes 0,1,2.
        """
        if not self.user_id:
            return
        try:
            modes = (mode_int,) if mode_int is not None else (0, 1, 2)
            with self.db.cursor() as cursor:
                for m in modes:
                    for idx, pname in enumerate(self.pose_names):
                        cursor.execute(
                            "SELECT id FROM record_detail WHERE user_id=%s AND posture_id=%s AND mode=%s LIMIT 1",
                            (self.user_id, idx, m)
                        )
                        exists = cursor.fetchone()
                        if not exists:
                            cursor.execute(
                                "INSERT INTO record_detail "
                                "(user_id, mode, total_posture_count, daily_max_app_opens, max_daily_usage_hours, "
                                "min_daily_usage_hours, longest_streak_days, posture_id, posture_name, total_completed, "
                                "max_accuracy, min_accuracy) "
                                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                (self.user_id, m, 0, 0, 0.0, 0.0, 0,
                                 idx, pname, 0, None, None)
                            )
            self.db.commit()
        except Exception:
            pass

    # --- utils ---------------------------------------------
    def _mode_to_int(self, mode):
        if isinstance(mode, int):
            return mode
        mapping = {"Practice": 0, "Easy": 1, "Hard": 2}
        if str(mode) == "ALL":
            return None
        return mapping.get(str(mode), 0)
    
    def _get_canonical_id(self, posture_id=None, posture_name=None):
        if posture_name:
            cname = self.pose_name_alias.get(posture_name, posture_name)
            if cname in self.pose_names:
                return self.pose_names.index(cname), cname
        if posture_id is not None and 0 <= posture_id < len(self.pose_names):
            return posture_id, self.pose_names[posture_id]
        return None, None
