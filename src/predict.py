from ultralytics import YOLO
import cv2

# 1. 加载你刚刚炼出来的“丹” (best.pt)
# 注意：路径里的 runs/detect/train 是你截图里显示的路径
model = YOLO('runs/detect/train/weights/best.pt') 

print("正在启动摄像头...按 'q' 键退出")

# 2. 调用摄像头进行预测 (source='0')
# conf=0.25: 把门槛调低点，只要有 25% 的把握就画框，方便看看它能不能认出那个只有 46 分的耳机头
results = model.predict(source='0', show=True, conf=0.25)