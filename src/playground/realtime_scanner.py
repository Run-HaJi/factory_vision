import cv2
import numpy as np

# --- 辅助函数：给 4 个点排序 (左上, 右上, 右下, 左下) ---
def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)] # 左上
    rect[2] = pts[np.argmax(s)] # 右下
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)] # 右上
    rect[3] = pts[np.argmax(diff)] # 左下
    return rect

# --- 主程序 ---
# 开启摄像头 (如果你有多个摄像头，尝试改 0 为 1)
cap = cv2.VideoCapture(0)

print("正在启动摄像头... 请拿一张【深色背景】上的【浅色矩形物体】(比如白纸/书本) 进行测试。")
print("按 'q' 键退出。")

while True:
    ret, frame = cap.read()
    if not ret:
        print("无法获取画面")
        break

    # 1. 【预处理】
    # 为了跑得快，先把图缩小一点 (可选，但推荐)
    # frame = cv2.resize(frame, (0, 0), fx=0.8, fy=0.8) 
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 高斯模糊：这一步极其重要！摄像头噪点多，不模糊一下 Canny 会疯掉
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # 边缘检测：阈值可以根据你的环境光线调整
    edged = cv2.Canny(blurred, 75, 200)

    # 2. 【找轮廓】
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 按面积从大到小排序，只取前 5 个，防止算力浪费
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    screenCnt = None # 用来存找到的"文档轮廓"

    # 3. 【筛选矩形】
    for c in cnts:
        # 计算周长
        peri = cv2.arcLength(c, True)
        # 多边形拟合
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # 如果拟合出来只有 4 个点，我们就认为它是矩形(文档)
        if len(approx) == 4:
            screenCnt = approx
            break # 找到了就退出循环

    # 4. 【如果有文档，就矫正】
    if screenCnt is not None:
        # A. 在原图上画个绿框，告诉你我瞄准了
        cv2.drawContours(frame, [screenCnt], -1, (0, 255, 0), 2)

        # B. 执行透视变换
        # reshape 变成 (4, 2)
        pts = screenCnt.reshape(4, 2)
        rect = order_points(pts)

        # 定义目标大小 (这里暂定 500x500 的正方形)
        # 实际项目中，你可以根据 rect 的长宽比动态计算
        maxWidth, maxHeight = 500, 500
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        # 变换矩阵
        M = cv2.getPerspectiveTransform(rect, dst)
        # 最终拉直的图
        warped = cv2.warpPerspective(frame, M, (maxWidth, maxHeight))

        # 显示拉直后的结果
        cv2.imshow("Scanned", warped)
    else:
        # 如果没找到，就把 Scanned 窗口关掉 (或者显示个黑屏)
        pass

    # 显示原始画面 (带绿框)
    cv2.imshow("Original", frame)
    # 显示边缘检测画面 (调试用，看看是不是光线太暗导致线断了)
    cv2.imshow("Edges", edged)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()