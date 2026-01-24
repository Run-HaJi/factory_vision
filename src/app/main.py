from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.core.engine import detector
import json
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select

# ===========================
# 1. 数据库定义 (The Memory)
# ===========================
class DetectionLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.now) # 自动记录时间
    object_class: str
    confidence: float
    is_alert: bool = Field(default=True)

# 创建 SQLite 数据库连接 (文件名为 factory_logs.db)
sqlite_file_name = "factory_logs.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# ===========================
# 2. FastAPI 应用初始化
# ===========================
app = FastAPI(title="Factory Vision API v2.0 (With Memory)")

# 启动时自动建表
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# CORS 配置 (保持不变)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================
# 3. WebSocket 管理器 (保持不变)
# ===========================
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"📱 新设备已连接！当前在线: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"📴 设备下线。")

    async def broadcast(self, message: dict):
        # 倒序遍历，防止移除时索引错误
        for connection in reversed(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"发送失败，移除死链接: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

# ===========================
# 4. 路由接口 (Routes)
# ===========================

@app.get("/")
def read_root():
    return {"status": "running", "db_status": "connected"}

# --- 新增：查询历史记录接口 ---
@app.get("/history", response_model=List[DetectionLog])
def get_history():
    """获取最近的 50 条报警记录"""
    with Session(engine) as session:
        # 按时间倒序查前50条
        statement = select(DetectionLog).order_by(DetectionLog.timestamp.desc()).limit(50)
        results = session.exec(statement).all()
        return results

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)

@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    if file.content_type and not file.content_type.startswith("image/"):
         raise HTTPException(status_code=400, detail=f"文件类型不对: {file.content_type}")

    try:
        contents = await file.read()
        results = detector.predict(contents, conf_threshold=0.25)
        
        # 🔥 核心逻辑升级：检测到 -> 广播 + 存库
        if results:
            top_result = results[0]
            
            # 1. 存入数据库 (Persistence)
            with Session(engine) as session:
                log = DetectionLog(
                    object_class=top_result['class'],
                    confidence=top_result['confidence']
                )
                session.add(log)
                session.commit()
                session.refresh(log) #以此获取自动生成的ID和时间
                print(f"💾 已存档: ID={log.id} Time={log.timestamp}")

            # 2. 发送 WebSocket 广播 (Notification)
            await manager.broadcast({
                "type": "detection_alert",
                "id": log.id,  # 把数据库ID也发过去
                "timestamp": log.timestamp.isoformat(),
                "count": len(results),
                "top_object": top_result['class'],
                "conf": top_result['confidence']
            })

        return {
            "filename": file.filename,
            "count": len(results),
            "detections": results
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))