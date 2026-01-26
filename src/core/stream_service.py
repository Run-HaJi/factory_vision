# src/core/stream_service.py

import cv2
import threading
import time
import asyncio
import os
import uuid
from datetime import datetime
from src.core.engine import detector

class RTSPMonitor:
    def __init__(self, rtsp_url, manager, loop, detection_interval=1.0):
        self.rtsp_url = rtsp_url
        self.manager = manager
        self.loop = loop
        self.interval = detection_interval
        self.running = False
        self.thread = None

    def start(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print(f"🚀 [RTSP] 工业视觉监控已启动: {self.rtsp_url}")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        print("🛑 [RTSP] 监控已停止")

    def _monitor_loop(self):
        cap = cv2.VideoCapture(self.rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        last_check_time = 0

        while self.running:
            ret, frame = cap.read()
            
            if not ret:
                print("⚠️ [RTSP] 信号丢失，3秒后重连...")
                cap.release()
                time.sleep(3)
                cap = cv2.VideoCapture(self.rtsp_url)
                continue

            current_time = time.time()
            if current_time - last_check_time < self.interval:
                time.sleep(0.05)
                continue
            
            last_check_time = current_time

            try:
                results = detector.predict(frame)

                if len(results) > 0:
                    top_result = results[0]
                    print(f"🚨 [ALERT] 发现目标: {top_result['class']} ({top_result['confidence']})")
                    self._trigger_alarm(frame, top_result)

            except Exception as e:
                print(f"❌ [RTSP] 检测线程出错: {e}")

        cap.release()

    def _trigger_alarm(self, frame, top_result):
        """
        报警处理：回归纯粹的文件路径模式
        """
        try:
            # 1. 画框
            annotated_frame = detector.model(frame)[0].plot()

            # 2. 生成文件名和保存路径
            # 确保文件名里没有奇怪字符
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = uuid.uuid4().hex[:6]
            filename = f"rtsp_{timestamp}_{unique_id}.jpg"
            
            # 存到磁盘 (Docker 里的 /app/static/images)
            os.makedirs("static/images", exist_ok=True)
            save_path = f"static/images/{filename}"
            cv2.imwrite(save_path, annotated_frame)
            
            # 3. 生成相对路径 (前端会自己拼接 IP)
            image_relative_url = f"/static/images/{filename}"

            # 4. 存库 + 广播
            from src.app.main import engine, DetectionLog
            from sqlmodel import Session
            
            with Session(engine) as session:
                log = DetectionLog(
                    object_class=top_result['class'],
                    confidence=top_result['confidence'],
                    image_url=image_relative_url
                )
                session.add(log)
                session.commit()
                session.refresh(log)

                # 5. 发送 WebSocket
                # 🔥 关键修改：不再发 Base64，而是发 image_relative_url
                # 这样前端处理逻辑就和“历史记录”完全一样了！
                message = {
                    "type": "detection_alert",
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "top_object": top_result['class'],
                    "conf": top_result['confidence'],
                    "image_url": image_relative_url  # 改回路径！
                }

                asyncio.run_coroutine_threadsafe(
                    self.manager.broadcast(message), 
                    self.loop
                )
            
        except Exception as e:
            print(f"❌ [RTSP] 报警处理失败: {e}")