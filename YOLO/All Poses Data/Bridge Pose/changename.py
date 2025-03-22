import os

def add_prefix_to_files(folder_path, prefix="a"):
    # 確保資料夾存在
    if not os.path.isdir(folder_path):
        print("資料夾不存在！")
        return
    
    # 取得資料夾內的所有檔案
    for filename in os.listdir(folder_path):
        old_path = os.path.join(folder_path, filename)
        
        # 確保是檔案（而非資料夾）
        if os.path.isfile(old_path):
            new_filename = prefix + filename
            new_path = os.path.join(folder_path, new_filename)
            os.rename(old_path, new_path)
            print(f"已重新命名: {filename} -> {new_filename}")

# 設定你的資料夾路徑，例如 "./data"
folder_path = r'C:\Users\lolJames\OneDrive\桌面\AI Yoga Coach\YOLO\All Poses Data\Bridge Pose\labels'  # 請替換成實際的資料夾路徑
add_prefix_to_files(folder_path)
