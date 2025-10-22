def get_plank_feedbackstr(scores: dict, threshold: int) -> tuple[bool, str]:
    feedbacks = []
    
    if scores.get("Arm_Bone", 100) < threshold:
        feedbacks.append("雙手手臂應伸直，避免彎曲")
    
    if scores.get("Body_Bone", 100) < threshold:
        feedbacks.append("身體應保持平直，避免臀部過高或過低")
    
    if scores.get("Triangle_bone", 100) < threshold:
        feedbacks.append("肩膀、手腕與腳踝應形成約90度的三角形")
    
    if len(feedbacks) > 0:
        return True, '\n'.join(feedbacks)
    else:
        return False, "Plank姿勢良好，請繼續保持！"
    