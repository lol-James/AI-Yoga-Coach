from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO(r'C:\Users\lolJames\OneDrive\桌面\AI Yoga Coach\YOLO\yolo11n.pt')
    
     
    model.train(data=r'C:\Users\lolJames\OneDrive\桌面\AI Yoga Coach\YOLO\data.yaml',
            mode="detect",
            epochs=200,
            imgsz=640,
            device=0)
    
