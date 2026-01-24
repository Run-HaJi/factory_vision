import albumentations as A
import cv2
import os
import glob
import shutil

# 1. 路径设置
# 原始数据在哪里
IMG_DIR = 'datasets/images'
LABEL_DIR = 'datasets/labels'

# 新数据存哪里 (我们建一个专门的增强数据集文件夹，保持原版干净)
OUT_IMG_DIR = 'datasets/aug_images'
OUT_LABEL_DIR = 'datasets/aug_labels'

# 如果文件夹不存在，自动创建
os.makedirs(OUT_IMG_DIR, exist_ok=True)
os.makedirs(OUT_LABEL_DIR, exist_ok=True)

# 2. 定义增强流水线 (加了 bbox_params 用来自动处理框)
transform = A.Compose([
    A.SafeRotate(limit=20, p=0.8, border_mode=cv2.BORDER_CONSTANT, value=0), # 旋转
    A.RandomBrightnessContrast(p=0.5), # 变亮变暗
    A.GaussNoise(p=0.3),               # 加噪点
    A.HorizontalFlip(p=0.5),           # 水平翻转
], bbox_params=A.BboxParams(format='yolo', min_visibility=0.3)) 
# format='yolo' 告诉它我们的 txt 是 yolo 格式的

def main():
    # 获取所有 jpg 图片
    img_paths = glob.glob(os.path.join(IMG_DIR, '*.jpg'))
    print(f"找到 {len(img_paths)} 张原始图片，准备生成增强数据...")

    for img_path in img_paths:
        # A. 读取图片
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, _ = image.shape

        # B. 读取对应的标签 txt
        # 比如 datasets/images/1.jpg -> datasets/labels/1.txt
        basename = os.path.basename(img_path) # 1.jpg
        name_only = os.path.splitext(basename)[0] # 1
        label_path = os.path.join(LABEL_DIR, name_only + '.txt')

        bboxes = []
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    # YOLO格式: class_id x y w h
                    parts = list(map(float, line.strip().split()))
                    # 把类别拿出来，剩下的 [x, y, w, h] 给 albumentations 处理
                    cls_id = int(parts[0])
                    bbox = parts[1:] + [cls_id] # 变成 [x, y, w, h, cls_id]
                    bboxes.append(bbox)

        # C. 每张图生成 5 张新图 (扩充 5 倍)
        for i in range(5):
            try:
                # 执行增强！魔法时刻！✨
                augmented = transform(image=image, bboxes=bboxes)
                aug_img = augmented['image']
                aug_bboxes = augmented['bboxes']

                # D. 保存结果
                # 新文件名：原名_aug_0.jpg
                new_name = f"{name_only}_aug_{i}"
                
                # 保存图片 (记得转回 BGR 否则颜色是反的)
                save_img_path = os.path.join(OUT_IMG_DIR, new_name + '.jpg')
                cv2.imwrite(save_img_path, cv2.cvtColor(aug_img, cv2.COLOR_RGB2BGR))

                # 保存标签 txt
                save_label_path = os.path.join(OUT_LABEL_DIR, new_name + '.txt')
                with open(save_label_path, 'w') as f:
                    for bbox in aug_bboxes:
                        # bbox 是 [x, y, w, h, cls_id]
                        # 我们要写回 txt 格式：cls_id x y w h
                        cls_out = int(bbox[-1])
                        coords = bbox[:-1]
                        line = f"{cls_out} {' '.join(map(str, coords))}\n"
                        f.write(line)
                
            except Exception as e:
                print(f"处理 {new_name} 时出错: {e}")

    print("✅ 数据增强完成！快去 datasets/aug_images 看看吧！")

if __name__ == '__main__':
    main()