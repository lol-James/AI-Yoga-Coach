def get_locust_feedbackstr(scores: dict, threshold: int) -> tuple[bool, str]:
    feedbacks = []

    if scores.get("Body_Bone", 100) < threshold:
        feedbacks.append("上半身應略為抬起，與地面夾角約25度")

    if scores.get("Knee_Bone", 100) < threshold:
        feedbacks.append("下半身應略為抬起，抬離地面約20度")

    if scores.get("Armpit_Bone", 100) < threshold:
        feedbacks.append("雙臂向後舉與地面平行")
    
    if scores.get("Head_Bone", 100) < threshold:
        feedbacks.append("上半身應保持直立")

    if feedbacks:
        return True, '\n'.join(feedbacks)
    else:
        if scores.get("average_score", 0) >= threshold:
            return False, "Locust姿勢良好，請繼續保持！"
        else:
            return False, "欸，怎麼會是0分？"