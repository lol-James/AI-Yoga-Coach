def get_staff_feedbackstr(scores: dict, threshold: int) -> tuple[bool, str]:
    feedbacks = []

    # Check hip bone (should sit upright on the floor)
    if scores.get("Hip_Bone", 100) < threshold:
        feedbacks.append("上半身應保持挺直，髖部需穩定貼地")

    # Check knee bone (legs should be straight)
    if scores.get("Knee_Bone", 100) < threshold:
        feedbacks.append("雙腿應完全伸直，避免膝蓋彎曲")

    # Return feedback summary
    if feedbacks:
        return True, '\n'.join(feedbacks)
    else:
        if scores.get("average_score", 0) >= threshold:
            return False, "Staff姿勢良好，請繼續保持！"
        else:
            return False, "欸，怎麼會是0分？"