from ultralytics import YOLO
import cv2

# 1. 加载模型
# 确保路径是对的
# 把 2 改成 3 👇
model = YOLO('runs/detect/train3/weights/best.pt')

# 2. 启动摄像头
cap = cv2.VideoCapture(0)

# 3. 降低门槛！
# 只要有 15% 的把握就画框，方便我们在这种背光条件下调试
CONF_THRESHOLD = 0.15 

print(f"摄像头已启动！检测阈值: {CONF_THRESHOLD}")
print("按 'q' 键退出...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 4. 让模型看图
    results = model(frame, conf=CONF_THRESHOLD)

    # 5. 把画好框的图拿回来
    annotated_frame = results[0].plot()

    # 6. 弹窗显示
    cv2.imshow("Factory Vision - Live", annotated_frame)

    # ---------------------------------------------------------
    # ⚠️ 关键修复：必须有这几行，窗口才会响应键盘！
    # waitKey(1) 表示等待 1 毫秒，看有没有按键输入      
    # ---------------------------------------------------------
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("正在退出...")
        break
    # ---------------------------------------------------------

# 释放资源
cap.release()
cv2.destroyAllWindows()