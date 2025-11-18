def get_bridge_feedbackstr(scores: dict, threshold: int) -> tuple[bool, str]:
    feedbacks = []
    
    if scores.get("Hip_Bone", 100) < threshold:
        feedbacks.append("髖部應抬高，使身體呈一直線")
    
    if scores.get("Knee_Bone", 100) < threshold:
        feedbacks.append("膝蓋略為彎曲，小腿垂直地面")
    
    if len(feedbacks) > 0:
        return True, '\n'.join(feedbacks)
    else:
        if scores.get("average_score", 0) >= threshold:
            return False, "Bridge姿勢良好，請繼續保持！"
        else:
            return False, "欸，怎麼會是0分？"