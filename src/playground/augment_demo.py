import albumentations as A
import cv2
import matplotlib.pyplot as plt

# 1. 定义增强流水线 (Pipeline)
# 这里就像是一个“滤镜组合包”
transform = A.Compose([
    # 随机旋转 (-30度 到 +30度)
    A.SafeRotate(limit=30, p=0.5),
    # 随机调整亮度及对比度
    A.RandomBrightnessContrast(p=0.5),
    # 随机加噪点 (模拟烂摄像头)
    A.GaussNoise(p=0.2),
    # 水平翻转
    A.HorizontalFlip(p=0.5),
])

def visualize(image):
    """用 Matplotlib 显示图片"""
    plt.figure(figsize=(10, 10))
    plt.axis('off')
    plt.imshow(image)
    plt.show()

# 2. 读取一张你的图片 (请确保路径对)
# 随便找一张你在 datasets/images 里拍的照片名字填进去
img_path = 'datasets/images/IMG_20260122_154033.jpg'  # <--- ⚠️ 这里要改成你实际的文件名
image = cv2.imread(img_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #以此转为RGB方便matplotlib显示

# 3. 疯狂生成 5 张增强后的图
print("开始生成增强预览...")
for i in range(5):
    # 调用增强器
    augmented = transform(image=image)['image']
    visualize(augmented)

    