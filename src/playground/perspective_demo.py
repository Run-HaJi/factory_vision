import cv2
import numpy as np

# 1. 读入图片
# 建议找一张稍微有点透视感的图，比如手机拍的电脑屏幕、书本、或者地板砖
# 如果没有，我们还是用代码造一张"假装倾斜"的图
img = np.zeros((450, 450, 3), dtype=np.uint8)

# 为了看出透视效果，我们画一个"梯形" (模拟斜着拍到的纸)
# 顺时针顺序：左上，右上，右下，左下
pts_src = np.float32([
    [100, 100],  # 左上 (原图里的位置)
    [350, 120],  # 右上 (有点歪)
    [400, 380],  # 右下 (离得很远，显得宽)
    [50, 380]    # 左下
])

# 画出这个梯形给你看
display_img = img.copy()
cv2.polylines(display_img, [np.int32(pts_src)], True, (0, 255, 0), 3)
cv2.imshow("Source (Tilted)", display_img)

# --- 核心逻辑开始 ---

# 2. 定义我们"希望"它变成什么样子 (上帝视角)
# 我们想要一个 300x300 的正方形
# 顺序必须和上面对应：左上，右上，右下，左下
pts_dst = np.float32([
    [0, 0],      # 映射到新图的左上角
    [300, 0],    # 右上角
    [300, 300],  # 右下角
    [0, 300]     # 左下角
])

# 3. 计算透视矩阵 (3x3 矩阵)
# 考点：这里用的是 getPerspectiveTransform，不是 Affine
M = cv2.getPerspectiveTransform(pts_src, pts_dst)

print("透视矩阵 (Homography Matrix):\n", M)

# 4. 执行变换 (Warp)
# 注意函数名变成了 warpPerspective
result = cv2.warpPerspective(img, M, (300, 300))

# 为了证明它变正了，我们在结果上画个网格
for i in range(0, 300, 30):
    cv2.line(result, (0, i), (300, i), (100, 100, 100), 1)
    cv2.line(result, (i, 0), (i, 300), (100, 100, 100), 1)

cv2.imshow("Result (Straight)", result)

cv2.waitKey(0)
cv2.destroyAllWindows()