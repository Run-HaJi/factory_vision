import cv2
import requests # 引入 HTTP 库
import time     # 引入时间库，用来做冷却计时
import json     # 用来把数据打包成 JSON 格式

def nothing(x):
    pass

# === 新增：网络报警函数 ===
def send_alarm(count, limit):
    # 模拟发送给 Node.js 后端的 JSON 数据
    # Java 里你可能要定义一个 DTO 类，这里直接写字典就行
    payload = {
        "device_id": "CAMERA_001",
        "error_type": "OVERLOAD",
        "current_count": count,
        "limit": limit,
        "timestamp": time.time()
    }
    
    # 目标网址 (这里用 httpbin.org 测试，实际就是你们公司的 http://192.168.x.x/api/alarm)
    url = "http://httpbin.org/post"
    
    try:
        print(f"🚀 正在上报数据: {payload} ...")
        # 发送 POST 请求，超时时间设为 1 秒，防止卡死视频
        response = requests.post(url, json=payload, timeout=1)
        
        if response.status_code == 200:
            print(f"✅ 上报成功！服务器回复: {response.status_code}")
        else:
            print(f"❌ 上报失败: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ 网络错误: {e}")

# ========================

cap = cv2.VideoCapture(0)

cv2.namedWindow('Control Panel')
cv2.createTrackbar('Threshold', 'Control Panel', 120, 255, nothing)
cv2.createTrackbar('Max Limit', 'Control Panel', 3, 10, nothing)

# 冷却时间控制
last_alarm_time = 0
COOLDOWN_SECONDS = 5 

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 图像处理流程
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    current_thresh = cv2.getTrackbarPos('Threshold', 'Control Panel')
    max_limit = cv2.getTrackbarPos('Max Limit', 'Control Panel')
    
    _, binary = cv2.threshold(blurred, current_thresh, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    product_count = 0 
    for contour in contours:
        if cv2.contourArea(contour) < 1000:
            continue
        product_count += 1 
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    status_text = f"Count: {product_count} / Limit: {max_limit}"
    
    # === 触发逻辑 ===
    if product_count > max_limit:
        # 视觉报警
        cv2.putText(frame, "WARNING: OVERLOAD!", (50, 200), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
        
        # === 网络报警 (带冷却检查) ===
        current_time = time.time()
        if current_time - last_alarm_time > COOLDOWN_SECONDS:
            # 触发 HTTP 请求
            send_alarm(product_count, max_limit)
            last_alarm_time = current_time # 重置计时器
            
    # 显示画面
    cv2.putText(frame, status_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('Control Panel', binary)
    cv2.imshow('Result', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()