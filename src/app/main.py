from fastapi import FastAPI, UploadFile, File, HTTPException
# 关键点：从 core 导入刚才写好的 detector
# 注意：Python 运行时的路径问题，稍后我会教你启动命令
from src.core.engine import detector 

app = FastAPI(title="Factory Vision API v1.0")

@app.get("/")
def read_root():
    return {"status": "running", "version": "1.0.0"}

@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    """
    业务端点：只处理 HTTP 协议，逻辑交给 Core
    """
    # 如果是 None，就先放行（或者加个 and 判断）
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(...)

    try:
        # 2. 读取数据
        contents = await file.read()
        
        # 3. 调用 Core 层干活
        results = detector.predict(contents, conf_threshold=0.25)
        
        # 4. 返回结果
        return {
            "filename": file.filename,
            "count": len(results),
            "detections": results
        }
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))