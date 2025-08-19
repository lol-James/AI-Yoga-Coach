import os
import shutil
import random

# 設定資料夾路徑（請修改為你的路徑）
base_dir = r"C:\Users\lolJames\OneDrive\桌面\AI Yoga Coach\YOLO\All Poses Data"  # 替換成你的 All Poses Data 資料夾路徑
dest_dir = r'C:\Users\lolJames\OneDrive\桌面\AI Yoga Coach\YOLO'  # 你要存放 train/valid/test 的資料夾

# 設定資料集比例
train_ratio = 0.7
valid_ratio = 0.2

def create_dirs():
    for split in ["train", "valid", "test"]:
        os.makedirs(os.path.join(dest_dir, split, "images"), exist_ok=True)
        os.makedirs(os.path.join(dest_dir, split, "labels"), exist_ok=True)

def split_data():
    for pose_folder in os.listdir(base_dir):
        pose_path = os.path.join(base_dir, pose_folder)
        images_path = os.path.join(pose_path, "images")
        labels_path = os.path.join(pose_path, "labels")
        
        if not os.path.isdir(images_path) or not os.path.isdir(labels_path):
            continue
        
        # 獲取所有圖片檔案
        image_files = [f for f in os.listdir(images_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        random.shuffle(image_files)  # 隨機排序
        
        # 計算切割數量
        total = len(image_files)
        train_count = int(total * train_ratio)
        valid_count = int(total * valid_ratio)
        test_count = total - train_count - valid_count
        
        # 分配到不同集合
        dataset_splits = {
            "train": image_files[:train_count],
            "valid": image_files[train_count:train_count + valid_count],
            "test": image_files[train_count + valid_count:]
        }
        
        # 複製圖片與標註檔案到對應的資料夾
        for split, files in dataset_splits.items():
            for image_file in files:
                image_src = os.path.join(images_path, image_file)
                label_src = os.path.join(labels_path, os.path.splitext(image_file)[0] + ".txt")
                
                image_dest = os.path.join(dest_dir, split, "images", image_file)
                label_dest = os.path.join(dest_dir, split, "labels", os.path.basename(label_src))
                
                shutil.copy(image_src, image_dest)
                if os.path.exists(label_src):
                    shutil.copy(label_src, label_dest)
                else:
                    print(f"⚠️ 找不到標註檔案：{label_src}")

# 執行
create_dirs()
split_data()
print("✅ 資料集分割完成！")
