# 🏭 Factory Vision 2.0 - Industrial IoT Real-time Monitoring System

> 基于边缘计算的工业视觉实时监控系统原型。集成 YOLOv8 目标检测、FastAPI 异步服务、WebSocket 实时通信与微信小程序移动端。

## 🌟 项目亮点 (Highlights)

* **⚡ 端边云协同**: 实现了 PC 边缘端 (YOLO) 与 移动端 (小程序) 的毫秒级联动。
* **📡 实时报警 (Real-time Alerts)**: 基于 WebSocket 协议，将视觉检测结果延迟控制在 200ms 以内。
* **💾 数据持久化 (Persistence)**: 内置 SQLite + SQLModel 轻量级时序数据库，自动归档报警记录。
* **📱 移动端监控**: 微信小程序客户端，支持状态可视化、震动报警与历史记录回溯。
* **🛡️ 抗干扰网络设计**: 针对局域网复杂环境（代理/防火墙）优化的穿透方案。

## 🏗️ 技术栈 (Tech Stack)

* **Core**: Python 3.10+
* **AI Engine**: Ultralytics YOLOv8
* **Backend**: FastAPI, Uvicorn
* **Database**: SQLite, SQLModel
* **Protocol**: WebSocket, HTTP/REST
* **Client**: WeChat Mini Program (WXML, WXSS, JS)

## 📂 项目结构 (Directory Structure)

```text
Factory_Vision_2.0/
├── .venv/                   # Python Virtual Environment
├── datasets/                # Training/Testing Datasets
├── factory_logs.db          # 💾 SQLite Database (Auto-generated)
├── requirements.txt         # Dependency List
├── src/                     # 🐍 Backend & AI Core
│   ├── app/
│   │   └── main.py          # 🔥 Main Entry (FastAPI + WebSocket)
│   ├── client/
│   │   ├── client.py        # Camera Simulator (Single Shot)
│   │   ├── batch_test.py    # Stress Testing Script
│   │   └── fake_phone.py    # WebSocket Debugger
│   └── core/
│       └── engine.py        # YOLO Inference Engine
└── wxapp/                   # 📱 WeChat Mini Program Source (Fixed)
    ├── pages/index/         # Monitoring Dashboard
    └── project.config.json  # WeChat DevTools Config

```

## 🚀 快速开始 (Quick Start)

### 1. 环境准备 (Prerequisites)

```bash
# 创建并激活虚拟环境
python -m venv .venv
# Windows Powershell 激活:
.\.venv\Scripts\Activate

# 安装依赖
pip install -r requirements.txt

```

### 2. 启动服务端 (Server Launch)

⚠️ **注意**: 必须使用 `0.0.0.0` 以允许局域网设备访问。

```bash
uvicorn src.app.main:app --reload --host 0.0.0.0

```

*启动成功后，服务端监听在 `http://0.0.0.0:8000*`

### 3. 配置微信小程序 (Client Setup)

1. 打开 **微信开发者工具**，导入 `wxapp` 文件夹。
2. 获取本机局域网 IP:
* 在终端运行 `ipconfig`。
* **关键**: 如果使用电脑开启热点，请寻找 **192.168.137.1** (通常为虚拟网卡 IP)。


3. 修改 `wxapp/pages/index/index.js`:
```javascript
// 替换为你的真实 IP
const wsUrl = "ws://192.168.137.1:8000/ws";
const apiUrl = "[http://192.168.137.1:8000/history](http://192.168.137.1:8000/history)";

```


4. 点击“编译”，确保显示“监控正常”。

### 4. 模拟触发 (Simulation)

保持小程序开启，运行客户端脚本发送测试图片：

```bash
python src/client/client.py

```

*预期效果：小程序震动、变红，并自动刷新历史记录列表。*

## 🛠️ 故障排查 (Troubleshooting)

如果手机/小程序无法连接服务端，请按以下顺序检查：

1. **防火墙**: 确保 Windows "公用网络" 防火墙已关闭。
2. **代理冲突 (Proxifier/VPN)**:
* 确保代理软件设置了 "Bypass LAN" (绕过局域网)。
* **微信开发者工具**: 设置 -> 代理设置 -> 必须选 **"不使用任何代理"**。


3. **调试基础库**: 如果小程序报错 `webapi_getwxasyncsecinfo:fail`，请在详情中将调试基础库降级至 `2.33.x` 或 `3.0.x`。

---

*Built with ❤️ by Tony Stark & J.A.R.V.I.S.*
