import cv2

# 1. 加载 OpenCV 自带的人脸识别模型 (Haar Cascade)
# 这个 xml 文件在安装 cv2 库时就已经在你的电脑里了，cv2.data.haarcascades 会自动找到路径
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# 加载眼睛识别模型 (可选，顺便玩玩)
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# 2. 打开摄像头
cap = cv2.VideoCapture(0)

print("正在启动人脸检测... 请看着摄像头。")
print("按 'q' 退出")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 转灰度 (Haar 特征是基于明暗的，不需要颜色)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 3. 【核心】开始识别人脸
    # scaleFactor=1.1: 每次扫描把窗口放大 10% (为了找不同大小的脸)
    # minNeighbors=5: 至少要有 5 个邻居也觉得这是脸，才算真的脸 (防误报)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    # 4. 把找到的脸画出来
    for (x, y, w, h) in faces:
        # 画蓝框
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # 搞点好玩的：在脸的区域里找眼睛
        # (这样能省算力，不用在全图找眼睛，只在脸上找)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex, ey, ew, eh) in eyes:
            # 画绿框
            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

    cv2.imshow('Face Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()