from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware  # 🔥 1. 导入这个库
from src.core.engine import detector
import json

app = FastAPI(title="Factory Vision API v1.0")

# 🔥 2. 配置 CORS (允许所有来源连接)
# 这一步非常关键！没有它，小程序和部分脚本连不上。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # "*" 表示允许任何 IP 连接
    allow_credentials=True,
    allow_methods=["*"],  # 允许任何方法 (GET, POST, WS...)
    allow_headers=["*"],  # 允许任何 Header
)

# --- 连接管理器 (保持不变) ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        # ⚠️ 必须先 accept，再加到列表里
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"📱 新设备已连接！当前在线: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"📴 设备下线。")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"发送失败，移除死链接: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

@app.get("/")
def read_root():
    return {"status": "running", "version": "1.0.0"}

# --- WebSocket 路由 (保持不变) ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接挂起，等待消息
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WS Error: {e}")
        manager.disconnect(websocket)

# --- 预测接口 (保持不变) ---
@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    if file.content_type and not file.content_type.startswith("image/"):
         raise HTTPException(status_code=400, detail=f"文件类型不对: {file.content_type}")

    try:
        contents = await file.read()
        results = detector.predict(contents, conf_threshold=0.25)
        
        # 如果有检测结果，广播报警
        if results:
            await manager.broadcast({
                "type": "detection_alert",
                "count": len(results),
                "top_object": results[0]['class'],
                "conf": results[0]['confidence']
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