from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO(r'C:\Users\lolJames\OneDrive\桌面\AI\Homework\FinalProject\yoga_data\yolov8n.pt')
    model.train(data=r'C:\Users\lolJames\OneDrive\桌面\AI\Homework\FinalProject\yoga_data\data.yaml',
                mode="detect",
                epochs=150,
                imgsz=640,
                device=0)