def get_downward_facing_dog_feedbackstr(scores: dict, threshold: int) -> tuple[bool, str]:
    feedbacks = []
    
    if scores.get("Arm_Bone", 100) < threshold:
        feedbacks.append("雙手手臂應伸直，避免彎曲")
    
    if scores.get("Hip_Bone", 100) < threshold:
        feedbacks.append("髖部應抬高，避免背部拱起來")
    
    if scores.get("Knee_Bone", 100) < threshold:
        feedbacks.append("雙腳應伸直，避免彎曲")
    
    if len(feedbacks) > 0:
        return True, '\n'.join(feedbacks)
    else:
        return False, "Downward Facing Dog姿勢良好，請繼續保持！"
    