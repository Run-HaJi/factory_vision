import cv2
import numpy as np

# 这是一个"全局变量"，用来存我们要旋转的原图
# 在真项目中尽量少用全局变量，但写 Demo 这样最省事
global_img = None

def rotate_image(val):
    angle = val
    h, w = global_img.shape[:2]
    center = (w // 2, h // 2)

    # 1. 先生成标准的旋转矩阵
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # --- 以下是新增的"防裁切"逻辑 ---

    # 2. 取出矩阵里的 cos 和 sin 值
    # M 矩阵长这样：[[cos, -sin, tx], [sin, cos, ty]]
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # 3. 算出新画布的长宽 (初中三角函数)
    # 新宽 = 原宽*cos + 原高*sin
    # 新高 = 原宽*sin + 原高*cos
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    # 4. 【关键】修正旋转中心
    # 如果不修正，图片旋转后会跑偏，甚至跑出画框
    # 这一步是把图片的中心，强行对齐到新画布的中心
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]

    # --- 逻辑结束 ---

    # 5. 执行变换
    # 注意：这里的 dsize (画布大小) 必须改成新的 (new_w, new_h)
    rotated_img = cv2.warpAffine(global_img, M, (new_w, new_h))
    
    cv2.imshow('Rotation Lab', rotated_img)

# --- 主程序入口 ---
if __name__ == "__main__":
    # 1. 造一张测试图 (400x400 的黑底)
    global_img = np.zeros((400, 400, 3), dtype=np.uint8)
    
    # 2. 画个白色箭头，方便看方向
    # 起点(200, 300) -> 终点(200, 100)，这是一根指向上方的箭头
    cv2.arrowedLine(global_img, (200, 300), (200, 100), (255, 255, 255), 8, tipLength=0.3)
    
    # 画个红框框住边缘，方便你观察"裁切"现象
    cv2.rectangle(global_img, (50, 50), (350, 350), (0, 0, 255), 2)

    # 3. 初始化窗口
    cv2.namedWindow('Rotation Lab')
    
    # 4. 创建滑块
    # 参数：滑块名, 窗口名, 默认值, 最大值, 回调函数
    cv2.createTrackbar('Angle', 'Rotation Lab', 0, 360, rotate_image)
    
    # 5. 先调用一次，显示初始状态
    rotate_image(0)
    
    # 6. 等待退出
    print("按 'q' 键退出程序")
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()