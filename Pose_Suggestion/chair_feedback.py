def get_chair_feedbackstr(scores: dict, threshold: int) -> tuple[bool, str]:
    feedbacks = []

    if scores.get("Knee_Bone", 100) < threshold:
        feedbacks.append("雙膝彎曲，角度約為90度")

    if scores.get("Hip_Bone", 100) < threshold:
        feedbacks.append("上半身向前傾，與大腿約呈120度")

    if scores.get("Armpit_Bone", 100) < threshold:
        feedbacks.append("雙臂向上舉並與身體成一條直線")
    
    if scores.get("Upperbody_Bone", 100) < threshold:
        feedbacks.append("上半身應保持直立")

    if feedbacks:
        return True, '\n'.join(feedbacks)
    else:
        if scores.get("average_score", 0) >= threshold:
            return False, "Chair姿勢良好，請繼續保持！"
        else:
            return False, "欸，怎麼會是0分？"
