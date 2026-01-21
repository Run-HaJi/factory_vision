# Factory Vision Learning 🏭

这是一个基于 **Python** 和 **OpenCV** 的机器视觉学习项目。
本项目旨在通过实践掌握计算机视觉的核心算法，并探索其在工业场景（如文档扫描、零件定位、缺陷检测）中的应用。

## 📂 项目结构

代码已重构至 `src/` 目录，保持根目录整洁。

```text
.
├── src/
│   ├── realtime_scanner.py   # [Boss战] 实时文档扫描与透视矫正系统
│   ├── auto_scan.py          # 静态图像的自动轮廓识别与矫正
│   ├── face_detect.py        # 基于 Haar 级联的人脸与眼部检测
│   ├── rotate_demo.py        # 图片旋转与自动 ROI 矫正 (解决裁切问题)
│   ├── perspective_demo.py   # 透视变换原理演示 (梯形 -> 正方形)
│   └── camera_test.py        # 基础摄像头调用测试
├── README.md                 # 项目说明文档
└── .gitignore                # Git 忽略配置
🚀 快速开始
1. 环境准备
确保已安装 Python 3.x 及以下依赖库：

Bash

pip install opencv-python numpy
(注意：运行 YOLO 相关代码需额外安装 ultralytics)

2. 运行脚本
由于代码位于 src 目录下，建议在根目录使用以下命令运行：

实时文档扫描仪（推荐体验）:

Bash

python src/realtime_scanner.py
操作提示：将深色背景上的浅色矩形物体（如书本、白纸）放置在摄像头前。

人脸检测:

Bash

python src/face_detect.py
图片旋转与防裁切实验:

Bash

python src/rotate_demo.py
🧠 核心知识点
本项目覆盖了以下 CV 核心概念：

形态学操作 (Morphology): 腐蚀、膨胀、开/闭运算 (用于降噪和修补)。

几何变换 (Geometry): 仿射变换 (旋转)、透视变换 (Perspective Transform)。

特征检测 (Features): Canny 边缘检测、轮廓查找 (FindContours)、多边形拟合 (ApproxPolyDP)。

实时处理: 摄像头视频流的 I/O 处理与帧率优化。

📝 待办列表 (To-Do)
[x] 基础图像处理 (色彩、形态学)

[x] 几何变换与矫正算法

[x] 传统特征检测 (Canny/Haar)

[ ] 集成 YOLO v8 实现通用物体识别 (Coming Soon...)

[ ] 接入工业缺陷检测实战案例