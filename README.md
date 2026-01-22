# Factory Vision Learning 🏭

这是一个基于 **Python** 和 **OpenCV** 的机器视觉学习项目。
本项目旨在通过实践掌握计算机视觉的核心算法，并探索其在工业场景（如文档扫描、零件定位、缺陷检测）中的应用。

---

## 📂 项目结构

代码已重构至 `src/` 目录，保持根目录整洁。

```text
.
├── src/
│   ├── yolo_demo.py          # [New] YOLOv8 实时目标检测 (80种通用物体)
│   ├── realtime_scanner.py   # 实时文档扫描与透视矫正系统
│   ├── auto_scan.py          # 静态图像的自动轮廓识别与矫正
│   ├── face_detect.py        # 基于 Haar 级联的人脸与眼部检测
│   ├── rotate_demo.py        # 图片旋转与自动 ROI 矫正 (解决裁切问题)
│   ├── perspective_demo.py   # 透视变换原理演示 (梯形 -> 正方形)
│   └── camera_test.py        # 基础摄像头调用测试
├── README.md                 # 项目说明文档
└── .gitignore                # Git 忽略配置

```

---

## 🚀 快速开始

### 1. 环境准备

确保已安装 Python 3.x 及以下依赖库：

```bash
pip install opencv-python numpy ultralytics

```

### 2. 运行脚本

由于代码位于 `src` 目录下，建议在**根目录**使用以下命令运行：

**🤖 YOLO 通用物体检测 (New):**

```bash
python src/yolo_demo.py

```

> *第一次运行会自动下载模型权重 (yolov8n.pt)，请保持网络通畅。*

**📷 实时文档扫描仪:**

```bash
python src/realtime_scanner.py

```

**👤 人脸检测:**

```bash
python src/face_detect.py

```

---

## 🧠 核心知识点

本项目覆盖了以下 CV 核心概念：

* **深度学习 (Deep Learning)**: YOLOv8 目标检测原理、卷积神经网络 (CNN) 应用。
* **形态学操作 (Morphology)**: 腐蚀、膨胀、开/闭运算 (用于降噪和修补)。
* **几何变换 (Geometry)**: 仿射变换 (旋转)、透视变换 (Perspective Transform)。
* **特征检测 (Features)**: Canny 边缘检测、轮廓查找 (FindContours)。

---

## 📝 待办列表 (To-Do)

* [x] 基础图像处理 (色彩、形态学)
* [x] 几何变换与矫正算法
* [x] 传统特征检测 (Canny/Haar)
* [x] **集成 YOLO v8 实现通用物体识别**
* [ ] **训练自定义模型 (工业缺陷检测)** (In Progress...)

---

*2026 Winter Internship Project*