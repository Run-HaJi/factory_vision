import cv2
import numpy as np

# 1. 造一张图：黑底，画一个白色的矩形
# 这里的 (300, 300) 是单通道图，不用 (300, 300, 3)，方便处理
img = np.zeros((300, 300), dtype=np.uint8)
cv2.rectangle(img, (50, 50), (250, 250), 255, -1) # -1 表示填满

# 2. 【搞破坏】撒盐 (添加随机噪点)
# 随机生成 1000 个噪点
for _ in range(1000):
    x = np.random.randint(0, 300)
    y = np.random.randint(0, 300)
    img[y, x] = 0 # 把背景变成黑/白点 (模拟灰尘)

# 这里你可以先 cv2.imshow 看看这张脏图，简直没法看

# 3. 【准备手术刀】定义核 (Kernel)
# 创建一个 5x5 的全 1 矩阵，这就是我们的"印章"
# 5x5 的意思是：我们会考虑每个像素周围 5x5 范围内的邻居
# kernel = np.ones((15, 15), np.uint8)

# 把那行 kernel = ... 换成这一行：
# MORPH_ELLIPSE 表示椭圆（也就是圆），(30, 30) 是尺寸
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (30, 30))

# 4. 【做手术】闭运算 (先膨胀，再腐蚀) - 专门用来填补内部黑洞
# 手动写法：
dilation = cv2.dilate(img, kernel, iterations=1) # 膨胀：白色区域扩张，吞噬内部黑洞
result = cv2.erode(dilation, kernel, iterations=1) # 腐蚀：外部轮廓缩回原样

# 高级写法 (直接调 API)：
# result = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

# 5. 显示对比
cv2.imshow('Dirty Source', img)
# cv2.imshow('Clean Source', erosion)
cv2.imshow('Clean Result', result)

cv2.waitKey(0)
cv2.destroyAllWindows()