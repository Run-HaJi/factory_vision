# src/app/main.py

import os
import cv2
import numpy as np
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from contextlib import asynccontextmanager # 🔥 新增：用于管理生命周期

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Field, Session, SQLModel, create_engine, select

# 导入我们的核心模块
from src.core.engine import detector
from src.core.stream_service import RTSPMonitor # 🔥 新增：导入刚才写的监控服务

# ===========================
# 1. 数据库定义
# ===========================
class DetectionLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=8))
    object_class: str
    confidence: float
    image_url: str = Field(default="")
    is_alert: bool = Field(default=True)

sqlite_file_name = "factory_logs.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# ===========================
# 2. WebSocket 管理器
# ===========================
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"📱 新设备已连接！在线: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print("📴 设备下线。")

    async def broadcast(self, message: dict):
        # 倒序发送，防止移除由于连接断开导致的索引问题
        for connection in reversed(self.active_connections):
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

# ===========================
# 3. 生命周期管理 (最关键的改动)
# ===========================
# 获取环境变量里的 RTSP 地址
RTSP_URL = os.getenv("RTSP_URL", None)
monitor_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- 启动阶段 (Startup) ---
    print("🚀 系统正在启动...")
    
    # 1. 初始化数据库
    create_db_and_tables()
    
    # 2. 确保静态文件目录存在
    os.makedirs("static/images", exist_ok=True)
    
    # 3. 启动 RTSP 监控 (如果有配置)
    global monitor_service
    if RTSP_URL:
        print(f"🎥 发现 RTSP 配置: {RTSP_URL}")
        loop = asyncio.get_running_loop()
        # 实例化监控服务，把 manager 和 loop 传进去
        monitor_service = RTSPMonitor(
            rtsp_url=RTSP_URL, 
            manager=manager, 
            loop=loop,
            detection_interval=2.0 # 每2秒检测一次
        )
        monitor_service.start()
    else:
        print("ℹ️ 未配置 RTSP_URL，运行在被动接收模式。")
    
    yield # 分界线，API 开始运行
    
    # --- 关闭阶段 (Shutdown) ---
    print("🛑 系统正在关闭...")
    if monitor_service:
        monitor_service.stop()

# ===========================
# 4. FastAPI 应用初始化
# ===========================
app = FastAPI(title="Factory Vision API v2.1 (RTSP Ready)", lifespan=lifespan)

# 挂载静态文件夹
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================
# 5. 路由接口
# ===========================

@app.get("/")
def read_root():
    return {
        "status": "running", 
        "mode": "RTSP Active" if monitor_service and monitor_service.running else "Passive",
        "rtsp_url": RTSP_URL
    }

@app.get("/history", response_model=List[DetectionLog])
def get_history():
    """获取最近 50 条记录"""
    with Session(engine) as session:
        statement = select(DetectionLog).order_by(DetectionLog.timestamp.desc()).limit(50)
        results = session.exec(statement).all()
        return results

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接活跃，如果需要接收前端指令可以在这里处理
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    # 1. 读取图片字节流
    contents = await file.read()
    
    # 2. 转换为 OpenCV 格式
    nparr = np.frombuffer(contents, np.uint8)
    img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 3. YOLO 推理
    results = detector.predict(img_cv2, conf_threshold=0.25)

    if results:
        top_result = results[0]
        
        # A. 使用 Ultralytics 绘图
        annotated_frame = detector.model(img_cv2)[0].plot()

        # B. 生成并保存图片
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.jpg"
        save_path = f"static/images/{filename}"
        cv2.imwrite(save_path, annotated_frame)
        
        # C. 生成相对 URL
        image_relative_url = f"/static/images/{filename}"

        # 4. 存入数据库
        with Session(engine) as session:
            log = DetectionLog(
                object_class=top_result['class'],
                confidence=top_result['confidence'],
                image_url=image_relative_url
            )
            session.add(log)
            session.commit()
            session.refresh(log)

        # 5. 发送广播
        await manager.broadcast({
            "type": "detection_alert",
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "top_object": top_result['class'],
            "conf": top_result['confidence'],
            "image_url": image_relative_url
        })

    # 🔥 修复返回值，满足 client.py 的需求
    return {
        "filename": file.filename,
        "count": len(results),
        "detections": results  # client.py 需要这个字段
    }