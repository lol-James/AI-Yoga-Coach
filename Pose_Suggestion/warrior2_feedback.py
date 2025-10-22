def get_warrior2_feedbackstr(scores: dict, threshold: int) -> tuple[bool, str]:
    feedbacks = []
    
    if scores.get("Arm_Bone", 100) < threshold:
        feedbacks.append("雙手手臂應伸直，避免彎曲")
    
    if scores.get("arm_body_bone", 100) < threshold:
        feedbacks.append("雙手手臂應與身體接近垂直")
    
    if scores.get("front_leg", 100) < threshold:
        feedbacks.append("前腳膝蓋應彎曲約90度，且膝蓋不超過腳尖")
    
    if scores.get("back_leg", 100) < threshold:
        feedbacks.append("後腳膝蓋應伸直，避免彎曲")
    
    if len(feedbacks) > 0:
        return True, '\n'.join(feedbacks)
    else:
        return False, "Warrior II姿勢良好，請繼續保持！"


