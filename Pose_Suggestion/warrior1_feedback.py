def get_warrior1_feedbackstr(scores: dict, threshold: int) -> tuple[bool, str]:
    feedbacks = []
    
    if scores.get("front_leg", 100) < threshold:
        feedbacks.append("前腳應彎曲形成直角")
    
    if scores.get("back_leg", 100) < threshold:
        feedbacks.append("後腳應伸直，避免彎曲")
    
    if scores.get("Front_Hip_Bone", 100) < threshold:
        feedbacks.append("軀幹與前腳應呈現垂直")
    
    if scores.get("Arm_Bone", 100) < threshold:
        feedbacks.append("雙手手臂應伸直，避免彎曲")
    
    if len(feedbacks) > 0:
        return True, '\n'.join(feedbacks)
    else:
        if scores.get("average_score", 0) >= threshold:
            return False, "Warrior I姿勢良好，請繼續保持！"
        else:
            return False, "欸，怎麼會是0分？"
    