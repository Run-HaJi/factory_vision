from ultralytics import YOLO
import cv2

# 1. 加载模型
# 第一次运行会自动从 GitHub 下载 'yolov8n.pt' (约6MB)，不用管它，等着就行
print("正在初始化 YOLOv8 模型...")
model = YOLO('yolov8n.pt') 

# 2. 开启实时检测
# source='0' 表示调用默认摄像头
# show=True 表示直接弹窗显示结果
# conf=0.5 表示只有置信度 > 50% 的才画框
print("摄像头推理启动中... 按 'Esc' 或 'q' 退出")
model.predict(source='0', show=True, conf=0.5)