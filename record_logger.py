import os
import json
from PyQt5.QtCore import QTimer
from datetime import datetime, timedelta

class RecordLogger:
    def __init__(self, ui, filename='pose_record.json'):
        self.ui = ui
        self.filename = filename
        self._session_start_time = datetime.now()
        self.ui.destroyed.connect(self._on_app_closed)

        # 姿勢順序對應統一
        self.pose_names = [
            "Bridge Pose",
            "Cow Pose",
            "Downward Facing Dog",
            "Locust Pose",
            "Plank Pose",
            "Squat Pose",
            "Staff Pose",
            "Triangle Pose",
            "Warrior I",
            "Warrior II"
        ]

        # label 對應設定
        self.pose_labels = {
            "Bridge Pose": self.ui.label_33,
            "Cow Pose": self.ui.label_55,
            "Downward Facing Dog": self.ui.label_37,
            "Locust Pose": self.ui.label_59,
            "Plank Pose": self.ui.label_61,
            "Squat Pose": self.ui.label_63,
            "Staff Pose": self.ui.label_65,
            "Triangle Pose": self.ui.label_67,
            "Warrior I": self.ui.label_69,
            "Warrior II": self.ui.label_71
        }

        if not os.path.exists(self.filename):
            self._init_file()

        # 從檔案載入紀錄並同步更新 UI
        self._sync_ui_from_file()

        # 儲存目前統計數值快照
        self.previous_counts = [self._get_tree_count(i) for i in range(10)]

        # 啟動定時監控
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._check_and_update)
        self.monitor_timer.start(1000)

    def _init_file(self):
        data = {
            "created": datetime.now().isoformat(),
            "total_count": 0,
            "records": {name: 0 for name in self.pose_names}
        }
        self._write_data(data)

    def _read_data(self):
        with open(self.filename, 'r') as f:
            return json.load(f)

    def _write_data(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)

    def _get_tree_count(self, index):
        try:
            return int(self.ui.statistics_treewidget.topLevelItem(index).text(1))
        except (ValueError, AttributeError):
            return 0

    def _sync_ui_from_file(self):
        """將 json 中的記錄值同步更新到 UI label 上"""
        data = self._read_data()
        total = data.get("total_count", 0)
        self.ui.label_18.setText(str(total))  # 更新總次數

        for pose, label in self.pose_labels.items():
            count = data["records"].get(pose, 0)
            label.setText(str(count))  # 更新對應 label

        self._update_max_min_labels()
        self._update_usage_summary()

    def _check_and_update(self):
        updated = False
        current_counts = []

        for i in range(10):
            count = self._get_tree_count(i)
            current_counts.append(count)

            if count > self.previous_counts[i]:
                pose_name = self.pose_names[i]
                self._add_record(pose_name)
                updated = True

        self.previous_counts = current_counts

        if updated:
            self._sync_ui_from_file()  # 若有更新就整體同步

    def _add_record(self, pose_name):
        data = self._read_data()
        if pose_name not in data["records"]:
            data["records"][pose_name] = 0
        data["records"][pose_name] += 1
        data["total_count"] += 1
        self._write_data(data)

    def reset_records(self):
        data = self._read_data()
        for name in data["records"]:
            data["records"][name] = 0
        data["total_count"] = 0
        self._write_data(data)
        self._sync_ui_from_file()

    def get_records(self):
        return self._read_data()

    def _update_max_min_labels(self):
        data = self._read_data()
        records = data["records"]

        # 避免全為 0 的狀況
        if not records:
            return

        # 找最大與最小（排除未出現的動作可視需求而定）
        max_pose = max(records, key=records.get)
        min_pose = min(records, key=records.get)

        max_count = records[max_pose]
        min_count = records[min_pose]

        # 更新 GUI
        self.ui.label_23.setText(max_pose)
        self.ui.label_31.setText(str(max_count))
        self.ui.label_25.setText(min_pose)
        self.ui.label_32.setText(str(min_count))
    
    def _on_app_closed(self):
        session_end = datetime.now()
        duration = round((session_end - self._session_start_time).total_seconds() / 3600, 2)  # 小時

        today_str = datetime.now().strftime("%Y-%m-%d")
        data = self._read_data()

        if "usage_log" not in data:
            data["usage_log"] = {}

        if today_str not in data["usage_log"]:
            data["usage_log"][today_str] = []

        data["usage_log"][today_str].append(duration)

        self._write_data(data)

    def _update_usage_summary(self):
        data = self._read_data()
        usage_log = data.get("usage_log", {})

        today = datetime.now().strftime("%Y-%m-%d")
        today_durations = usage_log.get(today, [])

        if today_durations:
            max_duration = max(today_durations)
            min_duration = min(today_durations)
        else:
            max_duration = min_duration = 0.0

        self.ui.label_73.setText(f"{max_duration:.2f}")
        self.ui.label_75.setText(f"{min_duration:.2f}")

        # 計算連續打卡天數
        date_list = sorted(usage_log.keys())
        max_streak = 0
        current_streak = 0
        prev_date = None

        for date_str in date_list:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if prev_date is None:
                current_streak = 1
            else:
                if (date_obj - prev_date).days == 1:
                    current_streak += 1
                else:
                    max_streak = max(max_streak, current_streak)
                    current_streak = 1
            prev_date = date_obj

        max_streak = max(max_streak, current_streak)
        self.ui.label_27.setText(str(max_streak))

        # 顯示使用總時數（單位：天）
        total_hours = sum(sum(day) for day in usage_log.values())
        total_days = total_hours / 24
        self.ui.label_21.setText(f"{total_days:.2f}")

        # 顯示一天最多啟動次數
        if usage_log:
            max_open_count = max(len(sessions) for sessions in usage_log.values())
        else:
            max_open_count = 0
        self.ui.label_29.setText(str(max_open_count))

