import os
import cv2
from ultralytics import YOLO

# 路徑設定
model_path = r"YOLO\runs\detect\train\weights\best.pt"
test_img_dir = r"YOLO\test\images"
test_label_dir = r"YOLO\test\labels"
result_dir = r"YOLO\test\results"

os.makedirs(result_dir, exist_ok=True)

# 載入模型
model = YOLO(model_path)

# 模型的 class 名稱 (對應 data.yaml)
class_names = ['Downward-Facing_Dog', 'Warrior_I', 'Warrior_II', 'Warrior_III',
               'Plank_Pose', 'Staff_Pose', 'Chair_Pose', 'Locust_Pose',
               'Triangle_Pose', 'Bridge_Pose']

wrong_images = []

# 遍歷測試圖片
for img_file in os.listdir(test_img_dir):
    if not img_file.lower().endswith(('.jpg', '.png', '.jpeg')):
        continue

    img_path = os.path.join(test_img_dir, img_file)
    label_path = os.path.join(test_label_dir, os.path.splitext(img_file)[0] + ".txt")

    # 推論
    results = model(img_path, verbose=False)

    # 預測結果 class IDs
    pred_classes = [int(box.cls[0]) for r in results for box in r.boxes]

    # 真實標籤
    true_classes = []
    if os.path.exists(label_path):
        with open(label_path, "r") as f:
            for line in f:
                cls_id = int(line.strip().split()[0])
                true_classes.append(cls_id)

    # 比對 (只比對有無正確 class，不嚴格比對 IOU)
    pred_set, true_set = set(pred_classes), set(true_classes)
    if pred_set != true_set:
        wrong_images.append(img_file)

    # 儲存框好的圖片
    for r in results:
        img_annotated = r.plot()
        cv2.imwrite(os.path.join(result_dir, img_file), img_annotated)

# 統計準確率
total = len(os.listdir(test_img_dir))
wrong = len(wrong_images)
correct = total - wrong

print(f"Total images: {total}")
print(f"Correct: {correct}")
print(f"Wrong: {wrong}")
print("Wrong images:")
for w in wrong_images:
    print(" -", w)
