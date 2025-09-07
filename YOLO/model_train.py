from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO(r'YOLO\yolo11n.pt')
    
     
    model.train(data=r'YOLO\data.yaml',
            mode="detect",
            epochs=200,
            imgsz=640,
            batch=64,
            device=0)
    
