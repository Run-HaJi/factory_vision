# Industrial Vision Inspector (工业视觉检测原型机)

这是一个基于 Python OpenCV 的工业视觉检测工具，主要用于产线零件计数与拥堵报警。

## 🛠 功能特性 (Features)
- **实时监控**: 调用工业/本地摄像头获取视频流。
- **视觉算法**: 集成 Canny 边缘检测与轮廓分析 (Blob Analysis)。
- **交互调试**: 支持通过 GUI 滑动条实时调整二值化阈值 (Threshold)。
- **智能报警**: 
  - 本地：当视野内零件数量超过设定上限，界面触发红色警报。
  - 云端：通过 HTTP POST 请求将异常数据上报至服务器 (IoT Integration)。

## 📦 环境依赖 (Requirements)
- Python 3.12+
- 核心库:
  - `opencv-python` (视觉处理)
  - `numpy` (矩阵运算)
  - `requests` (网络通信)

## 🚀 快速开始 (Quick Start)

### 1. 安装依赖
```bash
pip install -r requirements.txt