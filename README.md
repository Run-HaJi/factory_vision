# 🏭 Factory Vision V2.0 - 工业视觉检测系统 (Docker版)

> 基于 YOLOv8 + FastAPI + Docker 的轻量级边缘计算视觉检测系统，配备微信小程序实时监控端。

## 📖 项目简介
本项目模拟了一个工业流水线视觉检测场景。边缘端（Python/Docker）负责通过 YOLOv8 实时识别目标（如芯片、工件），并将检测结果与现场证据图通过 WebSocket 实时推送到微信小程序监控端。V2.0 版本全面容器化，实现了“一次构建，到处运行”。

## ✨ 核心特性 (V2.0 Updates)

- **🔥 工业级容器化部署**
  - 基于 Docker 封装运行环境，彻底解决 "It works on my machine" 问题。
  - 支持 Windows/Linux/MacOS 跨平台一键启动。

- **⚡ 高并发边缘计算架构**
  - 后端采用 FastAPI 异步框架，结合 WebSocket 实现毫秒级报警推送。
  - 针对 WSL2 环境进行了深度内存调优（Memory Limit + Swap），支持在 16GB 内存设备上稳定运行高频压测。

- **🕰️ 时空精准校准**
  - 内置时区修正机制，Docker 容器内部强制同步北京时间 (CST)，确保证据记录时间戳零误差。

- **📸 实时证据链**
  - 检测到异常目标时，自动截取现场画面并持久化存储。
  - 支持 Docker Volume 挂载，数据与代码实时同步，容器销毁数据不丢失。

## 🛠️ 技术栈

| 模块 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **核心算法** | YOLOv8 (Ultralytics) | 目标检测与置信度分析 |
| **后端服务** | FastAPI + Uvicorn | 高性能异步 Web 框架 |
| **数据存储** | SQLite + SQLModel | 轻量级单文件数据库，适合边缘端 |
| **容器化** | Docker + Docker Compose | 环境隔离与部署 |
| **前端监控** | 微信小程序 (WeChat) | 实时报警接收与历史回溯 |

## 📂 目录结构

```text
Factory_Vision2.0/
├── Dockerfile              # 🐳 容器构建描述文件
├── .dockerignore           # 构建忽略规则
├── .gitignore              # Git 忽略规则
├── src/
│   ├── app/                # FastAPI 服务端核心代码
│   │   ├── main.py         # 入口文件 & WebSocket 逻辑
│   │   └── models.py       # 数据库模型
│   ├── client/             # Python 模拟客户端 (压测用)
│   └── core/               # YOLO 推理引擎封装
├── weapp/                  # 📱 微信小程序源码
├── static/                 # [自动生成] 报警图片存储目录
├── factory_logs.db         # [自动生成] 历史记录数据库
└── requirements.txt        # Python 依赖清单

```

## 🚀 快速启动 (Quick Start)

### 1. 环境准备
- 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)。
- (可选) 建议配置 `.wslconfig` 限制 WSL2 内存占用，防止宿主机卡顿。

### 2. 构建镜像
在项目根目录下运行：
```bash
docker build -t factory-vision:v2 .

```

### 3. 启动容器 (挂载模式)

使用挂载模式启动，确保数据库和生成的图片可以直接同步到本地硬盘：

```bash
# 请将绝对路径 "D:\Projects\Factory_Vision2.0" 替换为你自己的实际路径
docker run --name factory-app -p 8000:8000 -v "D:\Projects\Factory_Vision2.0:/app" factory-vision:v2

```

### 4. 运行模拟客户端

开启一个新的终端，模拟摄像头发送检测请求：

```bash
# 单次测试
python src/client/client.py

# 压力测试 (PowerShell)
请在 VS Code 终端里先执行这一句（回车）：
$env:PYTHONIOENCODING="utf-8"

在终端输入：
# 🚀 50连发压测脚本 (UTF-8 修复版)
Write-Host "🚀 开始压测：50连发，间隔0.5秒..." -ForegroundColor Green

for ($i=1; $i -le 50; $i++) { 
    Write-Host "[第 $i 发] 正在识别..." -NoNewline;
    
    $start = Get-Date
    
    # 这里的 python 此时已经带着 UTF-8 buff 了
    python src/client/client.py | Out-Null
    
    $cost = ((Get-Date) - $start).TotalMilliseconds
    Write-Host " 完成! (耗时: $cost ms)" -ForegroundColor Yellow
    
    Start-Sleep -Milliseconds 500 
}

Write-Host "✅ 压测结束！" -ForegroundColor Green

```

## 📝 压测表现

* **硬件环境**: Windows 11 (WSL2), 16GB RAM + 16GB Virtual Memory
* **测试场景**: 50 次连续并发请求 (间隔 0.5s)
* **结果**: 服务端 0 报错，小程序实时响应无卡顿，Docker 内存占用稳定在 2GB-4GB 区间。

## 📜 License

MIT License

```

```