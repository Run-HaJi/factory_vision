# 🏭 Factory Vision V2.3: Industrial Edge AI Detection System

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)
![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688)
![YOLOv8](https://img.shields.io/badge/Model-YOLOv8-FF0066)
![RTSP](https://img.shields.io/badge/Protocol-RTSP%2FWebSocket-orange)

## 📖 项目简介 (Introduction)

**Factory Vision** 是一套轻量级、低延迟的**工业视觉边缘计算解决方案**。

该系统基于 **Docker 容器化架构**，能够主动拉取工业相机（或 IP 摄像头）的 **RTSP 视频流**，利用 **YOLOv8** 进行实时目标检测。一旦发现异常（如特定零件缺失、异物入侵），系统会在毫秒级内通过 **WebSocket** 推送报警信息至客户端（微信小程序），并实现证据图片的自动留存与审计。

> **核心价值**：将传统的“离线监控”升级为“实时智能感知”，实现 7x24 小时无人值守检测。

---

## 🏗️ 系统架构 (Architecture)

```mermaid
graph LR
    A[工业相机/IP Camera] -- RTSP Stream --> B(Docker Container)
    subgraph "Edge Server (Factory Vision V2.3)"
        B -- OpenCV Pull & Decode --> C{YOLOv8 Engine}
        C -- Inference (28ms) --> D[Logic Controller]
        D -- Save Image --> E[Local Storage / SQLite]
        D -- Async Broadcast --> F[FastAPI WebSocket]
    end
    F -- JSON + Image URL --> G[Client / WeChat Mini Program]

```

## 🚀 核心特性 (Key Features)

* **⚡ 实时流处理 (Real-time Processing)**:
* 集成 `Opencv` + `RTSP` 协议，支持断线自动重连。
* 优化 `CAP_PROP_BUFFERSIZE`，将端到端延迟控制在 **200ms 以内**。


* **🐳 容器化交付 (Dockerized)**:
* 基于 `python:3.10-slim` 构建，环境完全隔离。
* 通过 `Volume` 挂载实现数据持久化，通过环境变量配置 RTSP 源，真正做到“一次构建，到处运行”。


* **🔄 异步事件驱动 (Event-Driven)**:
* 利用 `FastAPI` 的 `lifespan` 管理后台守护线程。
* 通过 `asyncio` 和 `WebSocket` 实现检测线程与通信线程的解耦，确保高并发下的稳定性。


* **📱 全端闭环 (Full-Stack Loop)**:
* 后端实时推理 -> 数据库存证 -> 前端（小程序）实时弹窗报警，形成完整的业务闭环。



---

## 🛠️ 技术栈 (Tech Stack)

| 维度 | 技术选型 | 说明 |
| --- | --- | --- |
| **核心语言** | Python 3.10 | 工业界 AI 开发标准语言 |
| **AI 引擎** | Ultralytics YOLOv8 | SOTA 目标检测模型，自定义数据集训练 |
| **Web 框架** | FastAPI + Uvicorn | 高性能异步 Web 框架 |
| **计算机视觉** | OpenCV (Headless) | 视频流解码与图像预处理 |
| **基础设施** | Docker + WSL2 | 容器化部署与 Linux 兼容性层 |
| **通信协议** | RTSP / WebSocket / HTTP | 视频流传输与实时双工通信 |
| **持久化** | SQLite + SQLModel | 轻量级 ORM 数据库 |

---

## 🏁 快速开始 (Quick Start)

### 1. 环境准备

确保已安装 Docker Desktop。

### 2. 获取镜像

```bash
# 构建镜像 (确保网络畅通)
docker build -t factory-vision:v2.3 .

```

### 3. 启动容器

使用以下命令启动服务。请将 `RTSP_URL` 替换为实际摄像头的流地址。

```bash
# PowerShell / Bash
docker run -it --name factory-rtsp \
  -p 8000:8000 \
  -v "${PWD}:/app" \
  -e RTSP_URL="rtsp://admin:password@192.168.1.5:554/live" \
  factory-vision:v2.3

```

### 4. 验证运行

* **API 文档**: 访问 `http://localhost:8000/docs`
* **实时报警**: 观察终端日志输出 `🚨 [ALERT]`，或连接 WebSocket 客户端。

---

## 🔌 API 接口 (API Reference)

* `GET /`: 健康检查与运行模式状态。
* `GET /history`: 获取最近 50 条报警历史记录。
* `POST /predict`: (Legacy) 手动上传单张图片进行检测。
* `WS /ws`: WebSocket 端点，订阅实时报警流。

---

## 📅 版本历史 (Changelog)

* **V2.3 (Current)**:
* ✅ 新增 RTSP 视频流自动拉取与断线重连。
* ✅ 统一实时报警与历史记录的数据格式（基于 URL 路径）。
* ✅ 修复 Docker 网络与宿主机通信问题。


* **V2.0**:
* ✅ 引入 Docker 容器化部署。
* ✅ 增加 SQLite 数据库与持久化存储。
* ✅ 集成 WebSocket 实时推送。


* **V1.0**:
* ✅ 基础 YOLOv8 模型训练与推理脚本。
* ✅ 简单的 HTTP 接口。



---

## 👨‍💻 开发者 (Credits)

**Lead Developer**: Run-Haji
  * *Role*: Architecture Design, Core Implementation, Hardware Integration
**AI Co-pilot**: Google Gemini 3.0 Pro
  * *Role*: Technical Consultant, Code Optimization, Debugging Partner
**Status**: 🚀 V2.3 Stable Release

---