import os

# 設定主資料夾路徑（請修改為你的資料夾位置）
base_dir = r"C:\code\專題\app\AI-Yoga-Coach\YOLO\All Poses Data"  # 替換成你的根目錄

# 紀錄沒有標註檔的圖片
missing_labels = []

# 遍歷每個姿勢的資料夾
for pose_folder in os.listdir(base_dir):
    pose_path = os.path.join(base_dir, pose_folder)
    images_path = os.path.join(pose_path, "images")
    labels_path = os.path.join(pose_path, "labels")
    
    # 確保 images 和 labels 資料夾存在
    if not os.path.isdir(images_path) or not os.path.isdir(labels_path):
        continue
    
    # 檢查每張圖片是否有對應的標註檔
    for image_file in os.listdir(images_path):
        if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_name = os.path.splitext(image_file)[0]  # 去除副檔名
            label_file = f"{image_name}.txt"
            label_path = os.path.join(labels_path, label_file)
            
            if not os.path.exists(label_path):
                missing_labels.append(os.path.join(images_path, image_file))

# 輸出沒有標註檔的圖片
if missing_labels:
    print("以下圖片沒有對應的標註檔：")
    for img in missing_labels:
        print(img)
else:
    print("所有圖片都有對應的標註檔！")
