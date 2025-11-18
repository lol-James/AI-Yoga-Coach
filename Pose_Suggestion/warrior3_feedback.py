def get_warrior3_feedbackstr(scores: dict, threshold: int) -> tuple[bool, str]:
    feedbacks = []

    if scores.get("Arm_Bone", 100) < threshold:
        feedbacks.append("雙手手臂應伸直，避免彎曲")

    # Hip feedback (left/right)
    if scores.get("Hip_Bone_Left", 100) < threshold:
        feedbacks.append("抬高左腿向後伸直，讓身體與左腿保持一直線")
    if scores.get("Hip_Bone_Right", 100) < threshold:
        feedbacks.append("抬高右腿向後伸直，讓身體與右腿保持一直線")

    # Knee feedback
    if scores.get("Knee_Bone", 100) < threshold:
        feedbacks.append("雙腳應伸直，避免膝蓋彎曲")

    if feedbacks:
        return True, '\n'.join(feedbacks)
    else:
        if scores.get("average_score", 0) >= threshold:
            return False, "Warrior III姿勢良好，請繼續保持！"
        else:
            return False, "欸，怎麼會是0分？"