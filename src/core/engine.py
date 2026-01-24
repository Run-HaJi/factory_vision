from ultralytics import YOLO
import cv2
import numpy as np

class AIEngine:
    """
    AI 核心引擎：负责模型的加载和推理逻辑
    单例模式 (Singleton) 建议：在模块级别初始化实例
    """
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        try:
            print(f"🔄 [Core] 正在加载模型: {model_path} ...")
            self.model = YOLO(model_path)
            print(f"✅ [Core] 模型加载完毕！")
        except Exception as e:
            print(f"❌ [Core] 模型加载失败: {e}")
            raise e

    def predict(self, image_data, conf_threshold=0.25):
        # 🔥 V2.0 核心升级：智能兼容层
        # 既支持 raw bytes (来自旧接口)，也支持 numpy array (来自新绘图接口)
        
        img = None
        
        # 1. 智能解析
        if isinstance(image_data, np.ndarray):
            # 如果已经是 numpy 数组 (OpenCV 图)，直接用
            img = image_data
        elif isinstance(image_data, bytes):
            # 如果是字节流，解码成图片
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
        # 2. 安全检查
        if img is None:
            raise ValueError("无法解析图像数据")

        # 3. 推理 (Inference)
        results = self.model(img, conf=conf_threshold)
        
        # 4. 结果格式化
        detections = []
        for r in results:
            for box in r.boxes:
                # 获取类别 ID 和 名称
                cls_id = int(box.cls[0])
                cls_name = self.model.names[cls_id]
                conf = float(box.conf[0])
                
                # 封装结果
                detections.append({
                    "class": cls_name,
                    "confidence": round(conf, 2),
                    "box": box.xyxy[0].tolist() # 坐标，虽然前端还没用，先存着
                })
        
        return detections

# --- 单例初始化 ---
# 这里硬编码路径，或者从配置文件读取。
# 确保这个路径相对于你运行 python 命令的根目录是对的
MODEL_PATH = 'runs/detect/train3/weights/best.pt' 

# 全局单例，外部直接 import 这个 detector
detector = AIEngine(MODEL_PATH)