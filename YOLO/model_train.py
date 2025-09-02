from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO(r'AI-Yoga-Coach\YOLO\yolo11n.pt')
    
     
    model.train(data=r'AI-Yoga-Coach\YOLO\data.yaml',
            mode="detect",
            epochs=200,
            imgsz=640,
            batch=-1,
            device=0)
    
