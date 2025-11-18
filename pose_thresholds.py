from yoga_pose_calculate import PoseCalculate

# Threshold scores for each yoga pose
POSE_THRESHOLDS = {
    "bridge": {"Easy": 88, "Hard": 98},
    "chair": {"Easy": 78, "Hard": 90},
    "downward_facing_dog": {"Easy": 83, "Hard": 94},
    "locust": {"Easy": 80, "Hard": 90},
    "plank": {"Easy": 85, "Hard": 94},
    "staff": {"Easy": 86, "Hard": 94},
    "triangle": {"Easy": 82, "Hard": 91},
    "warrior1": {"Easy": 72, "Hard": 87},
    "warrior2": {"Easy": 83, "Hard": 91},
    "warrior3": {"Easy": 77, "Hard": 88},
}

def is_pose_score_valid(pose_index, avg_score, mode):
    # Determine whether the current score meets the mode requirements
    
    pose_key = PoseCalculate.INDEX_TO_KEY.get(pose_index)
    if pose_key is None or avg_score <= 0:
        return False

    if mode == "Practice":
        return True  # Always show score

    if mode in ["Easy", "Hard"] and pose_key in POSE_THRESHOLDS:
        return avg_score >= POSE_THRESHOLDS[pose_key][mode]

    return False
# Displays the standard score of the current posture in this mode
def display_standard_score(label_widget, pose_name, mode):
    pose_key = (pose_name.lower()
                .replace("_pose", "")
                .replace("-", "_")
                .replace(" ", ""))

    #針對三個warrior指向pose_name的key進行例外處理
    if "warrior" in pose_key:
        pose_key = pose_key.replace("_", "")
        pose_key = (pose_key
                    .replace("warrioriii", "warrior3")
                    .replace("warriorii", "warrior2")
                    .replace("warriori", "warrior1"))

    raw_name = pose_name.replace("_", " ").replace("-", " ")
    if "warrior" in raw_name.lower():
        if "iii" in raw_name.lower():
            display_name = "Warrior 3"
        elif "ii" in raw_name.lower():
            display_name = "Warrior 2"
        elif "i" in raw_name.lower():
            display_name = "Warrior 1"
        else:
            display_name = "Warrior"
    else:
        display_name = raw_name.title()

    mode_key = mode.capitalize().strip()

    if pose_key in POSE_THRESHOLDS and mode_key in POSE_THRESHOLDS[pose_key]:
        standard = POSE_THRESHOLDS[pose_key][mode_key]
        label_widget.setText(f"{display_name} ({mode_key}) : {standard}")
    else:
        label_widget.setText("Undefined pose or mode")

