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

    def predict(self, image_bytes: bytes, conf_threshold: float = 0.25):
        """
        核心推理函数
        :param image_bytes: 图片二进制数据
        :param conf_threshold: 置信度阈值
        :return: 格式化后的检测结果列表
        """
        # 1. 图像预处理 (Bytes -> OpenCV Image)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("无法解析图像数据")

        # 2. 模型推理
        results = self.model(img, conf=conf_threshold)

        # 3. 结果格式化 (清洗数据，只返回纯净的 Python 对象)
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                detections.append({
                    "class": self.model.names[int(box.cls[0])],
                    "confidence": round(float(box.conf[0]), 2),
                    "bbox": box.xyxy[0].tolist()
                })
        
        return detections

# --- 单例初始化 ---
# 这里硬编码路径，或者从配置文件读取。
# 确保这个路径相对于你运行 python 命令的根目录是对的
MODEL_PATH = 'runs/detect/train3/weights/best.pt' 

# 全局单例，外部直接 import 这个 detector
detector = AIEngine(MODEL_PATH)