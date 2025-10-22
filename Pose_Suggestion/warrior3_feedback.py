def get_warrior3_feedbackstr(scores: dict, threshold: int) -> tuple[bool, str]:
    feedbacks = []

    if scores.get("Arm_Bone", 100) < threshold:
        feedbacks.append("雙手手臂應伸直，避免彎曲")

    # Hip feedback (left/right)
    if scores.get("Hip_Bone_Left", 100) < threshold:
        feedbacks.append("左側髖部伸直，右側膝蓋彎曲約90°")
    if scores.get("Hip_Bone_Right", 100) < threshold:
        feedbacks.append("右側髖部伸直，左側膝蓋彎曲約90°")

    # Knee feedback
    if scores.get("Knee_Bone", 100) < threshold:
        feedbacks.append("雙腳應伸直，避免膝蓋彎曲")

    if feedbacks:
        return True, '\n'.join(feedbacks)
    else:
        return False, "Warrior III姿勢良好，請繼續保持！"
