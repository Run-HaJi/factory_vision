import cv2
import numpy as np

# 1. 造图：还是用刚才那个梯形图，因为背景纯黑，好识别
img = np.zeros((450, 450, 3), dtype=np.uint8)
pts_src = np.array([[100, 100], [350, 120], [400, 380], [50, 380]], dtype=np.int32)
# 画一个实心的白色梯形 (255,255,255)，方便做边缘检测
cv2.fillPoly(img, [pts_src], (255, 255, 255))

cv2.imshow("Source", img)

# 2. 【核心】Canny 边缘检测
# 灰度化：Canny 只能处理单通道图
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 两个阈值：
# 低于 50 的被认为是噪点，丢弃
# 高于 150 的被认为是强边缘，保留
# 50-150 之间的，如果连着强边缘就保留，否则丢弃
edges = cv2.Canny(gray, 50, 150)

cv2.imshow("Canny Edges", edges) # 你会看到一个空心的白框

# 3. 【核心】查找轮廓 (Find Contours)
# 这一步是把 Canny 找到的白点，连成一条条“线段对象”
# mode=cv2.RETR_EXTERNAL: 只找最外面的轮廓 (如果有空洞也不管)
# method=cv2.CHAIN_APPROX_SIMPLE: 压缩轮廓 (一条直线只存起点和终点，省内存)
contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"找到了 {len(contours)} 个轮廓")

# 4. 在原图上画出轮廓
# -1 表示画所有轮廓，(0, 255, 0) 是绿色，2 是粗细
cv2.drawContours(img, contours, -1, (0, 255, 0), 2)

cv2.imshow("Auto Detected", img)

# --- 接上面的代码 ---

# 我们取面积最大的轮廓（防止以后有噪点干扰，取最大的肯定是梯形）
# key=cv2.contourArea 表示按面积排序
c = sorted(contours, key=cv2.contourArea, reverse=True)[0]

# 1. 【核心】多边形拟合 (找角点)
# 计算轮廓周长
peri = cv2.arcLength(c, True)
# 0.02 * peri 是精度。意思是：拟合出来的线，跟原轮廓的最大误差不能超过周长的 2%
# 这样能忽略掉边缘的小锯齿，直接得到 4 个角的坐标
approx = cv2.approxPolyDP(c, 0.02 * peri, True)

print(f"拟合后的角点数量: {len(approx)}")

if len(approx) == 4:
    # 拿到 4 个顶点坐标 (此时顺序是乱的，可能是左下开头，也可能是右上开头)
    # reshape(4, 2) 是把数据变成 [[x1,y1], [x2,y2]...] 的格式
    pts = approx.reshape(4, 2)
    
    # --- 2. 【难点】给 4 个点排序 ---
    # 我们需要的顺序必须是：左上 -> 右上 -> 右下 -> 左下
    # 不排序的话，图可能会被扭成麻花
    rect = np.zeros((4, 2), dtype="float32")

    # 左上角：x+y 最小；右下角：x+y 最大
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)] # 左上
    rect[2] = pts[np.argmax(s)] # 右下

    # 右上角：y-x 最小；左下角：y-x 最大
    # (注意：这个简易算法在极端倾斜时可能失效，但对一般梯形够用了)
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)] # 右上
    rect[3] = pts[np.argmax(diff)] # 左下

    print("自动识别出的 4 个角:\n", rect)

    # --- 3. 执行透视变换 (和之前一样) ---
    # 目标：变成 300x300 的正方形
    width, height = 300, 300
    dst = np.array([
        [0, 0],
        [width, 0],
        [width, height],
        [0, height]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, M, (width, height))

    # 显示最终结果
    cv2.imshow("Final Auto Scanned", warped)
    
else:
    print("识别失败！没找到 4 个角，可能不是四边形。")

cv2.waitKey(0)
cv2.destroyAllWindows()