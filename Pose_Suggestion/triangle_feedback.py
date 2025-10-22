def get_triangle_feedbackstr(scores: dict, threshold: int) -> tuple[bool, str]:
    feedbacks = []
    
    if scores.get("Trunk", 100) < threshold:
        feedbacks.append("身體與垂直軸形成更大的夾角")
    
    if scores.get("Pelvis", 100) < threshold:
        feedbacks.append("雙腳張開，與肩同寬")
    
    if scores.get("Shoulder", 100) < threshold:
        feedbacks.append("兩手平行伸直，與地面垂直")
    
   
    if len(feedbacks) > 0:
        return True, '\n'.join(feedbacks)
    else:
        return False, "Triangle 姿勢良好，請繼續保持！"