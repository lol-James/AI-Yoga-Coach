def get_locust_feedbackstr(scores: dict, threshold: int) -> tuple[bool, str]:
    feedbacks = []

    if scores.get("Body_Bone", 100) < threshold:
        feedbacks.append("上半身應略為抬起，避免過高或過低")

    if scores.get("Knee_Bone", 100) < threshold:
        feedbacks.append("下半身應略為抬起，避免過高或過低")

    if scores.get("Armpit_Bone", 100) < threshold:
        feedbacks.append("雙臂向後舉與地面平行")
    
    if scores.get("Head_Bone", 100) < threshold:
        feedbacks.append("上半身應保持直立")

    if feedbacks:
        return True, '\n'.join(feedbacks)
    else:
        return False, "Locust姿勢良好，請繼續保持！"