from yoga_pose_calculate import INDEX_TO_KEY

# Threshold scores for each yoga pose
POSE_THRESHOLDS = {
    "bridge": {"Easy": 88, "Hard": 95},
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
    
    pose_key = INDEX_TO_KEY.get(pose_index)
    if pose_key is None or avg_score <= 0:
        return False

    if mode == "Practice":
        return True  # Always show score

    if mode in ["Easy", "Hard"] and pose_key in POSE_THRESHOLDS:
        return avg_score >= POSE_THRESHOLDS[pose_key][mode]

    return False
