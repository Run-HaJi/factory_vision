from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # 🔥 新增：用于提供静态文件服务
from src.core.engine import detector
import json
import cv2
import numpy as np
import os
import uuid
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select

# ===========================
# 1. 数据库定义 (升级版：带图片路径)
# ===========================
class DetectionLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.now)
    object_class: str
    confidence: float
    image_url: str = Field(default="")  # 🔥 新增：存图片的相对路径
    is_alert: bool = Field(default=True)

# 数据库连接
sqlite_file_name = "factory_logs.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# ===========================
# 2. FastAPI 应用初始化
# ===========================
app = FastAPI(title="Factory Vision API v2.0 (With Visuals)")

# 🔥 关键步骤：挂载 static 文件夹
# 这样你就能通过 http://ip:8000/static/images/xxx.jpg 访问图片了
os.makedirs("static/images", exist_ok=True) # 确保文件夹存在
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================
# 3. WebSocket 管理器 (不变)
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
        for connection in reversed(self.active_connections):
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

# ===========================
# 4. 路由接口
# ===========================

@app.get("/")
def read_root():
    return {"status": "running", "visual_module": "active"}

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
            await websocket.receive_text()
    except:
        manager.disconnect(websocket)

@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    # 1. 读取图片字节流
    contents = await file.read()
    
    # 2. 转换为 OpenCV 格式 (为了能画图)
    nparr = np.frombuffer(contents, np.uint8)
    img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 3. YOLO 推理
    results = detector.predict(img_cv2, conf_threshold=0.25) # 传入 CV2 对象

    if results:
        top_result = results[0]
        
        # 🔥🔥🔥 视觉核心逻辑 🔥🔥🔥
        
        # A. 使用 Ultralytics 自带的绘图功能 (画框、画标签)
        # plot() 返回一个 BGR 的 numpy 数组，就是画好框的图
        annotated_frame = detector.model(img_cv2)[0].plot()

        # B. 生成唯一文件名 (防止覆盖)
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.jpg"
        save_path = f"static/images/{filename}"
        
        # C. 保存图片到磁盘
        cv2.imwrite(save_path, annotated_frame)
        
        # D. 生成相对 URL (发给小程序用)
        image_relative_url = f"/static/images/{filename}"

        # 4. 存入数据库
        with Session(engine) as session:
            log = DetectionLog(
                object_class=top_result['class'],
                confidence=top_result['confidence'],
                image_url=image_relative_url  # 存进去！
            )
            session.add(log)
            session.commit()
            session.refresh(log)

        # 5. 发送广播 (带上图片 URL)
        await manager.broadcast({
            "type": "detection_alert",
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "top_object": top_result['class'],
            "conf": top_result['confidence'],
            "image_url": image_relative_url  # 发过去！
        })

    return {"count": len(results)}