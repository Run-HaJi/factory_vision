from ultralytics import YOLO

def main():
    # 1. 加载模型
    # 我们用 nano 版本 (v8n)，它是最小最快的，适合笔记本跑
    print("正在加载 YOLOv8n 模型...")
    model = YOLO('yolov8n.pt') 

    # 2. 开始训练 (The Magic Happens Here)
    # data: 指向咱们刚才写的 data.yaml
    # epochs: 训练多少轮 (50轮对于只有十几张图的数据集足够了)
    # imgsz: 图片大小 (640 是标准)
    # device: 'cpu' (如果没有显卡就用CPU，如果你有N卡可以改成 '0')
    print("开始训练工厂缺陷检测模型... 🚀")
    model.train(
        data='data.yaml', 
        epochs=50, 
        imgsz=640,
        device='cpu',   # 如果你有 NVIDIA 显卡并装了 CUDA，把它删掉，速度会快10倍
        workers=0       # Windows 下必须设为 0，否则会报错
    )

    # 3. 导出模型
    # 训练好的模型会自动保存在 runs/detect/train/weights/best.pt
    print("训练完成！模型已保存。")

if __name__ == '__main__':
    main()