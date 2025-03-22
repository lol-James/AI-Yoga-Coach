from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO(r'C:\Users\lolJames\OneDrive\桌面\AI Yoga Coach\YOLO\yolo11n.pt')
    
    # train01    
    # model.train(data=r'C:\Users\lolJames\OneDrive\桌面\AI Yoga Coach\YOLO\data.yaml',
    #         mode="detect",
    #         epochs=200,
    #         imgsz=640,
    #         device=0)
    
    # train02
    model.train(
        data=r'C:\Users\lolJames\OneDrive\桌面\AI Yoga Coach\YOLO\data.yaml',
        mode="detect",
        epochs=200,        
        imgsz=640,         # 影像尺寸
        batch=16,          # 增加 batch size，提高 GPU 使用率
        device=0,          # 使用 GPU 訓練
        optimizer="AdamW", # AdamW 優化器，提升準確率
        lr0=0.0015,        # 降低初始學習率
        lrf=0.1,           # 最終學習率
        momentum=0.937,    # 動量
        weight_decay=0.0005,# 防止過擬合
        amp=False,         # 若顯存不夠，可開啟 AMP（混合精度）
        cos_lr=True,       # 使用餘弦退火學習率
        mosaic=0.8,        # 降低 Mosaic 強度
        mixup=0.1,         # 減少 MixUp
        hsv_h=0.01, hsv_s=0.5, hsv_v=0.3, # 降低顏色變換
        dropout=0.05       # 適量增加 Dropout，防止過擬合
    )