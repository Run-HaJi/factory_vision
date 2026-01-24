import requests
import os

# 1. 你的 API 地址
API_URL = "http://127.0.0.1:8000/predict"

# 2. 要测试的图片路径 (保持你原来的路径)
image_path = "datasets/images/IMG_20260123_105038.jpg" 

def call_api(img_path):
    print(f"📡 正在发送图片: {img_path} ...")
    
    # 获取文件名 (比如 "IMG_20260123_105038.jpg")
    filename = os.path.basename(img_path)

    # 打开图片文件
    with open(img_path, "rb") as f:
        # -----------------------------------------------------------
        # ⚠️ 关键修改在这里！
        # 格式是: "参数名": (文件名, 文件对象, MIME类型)
        # 显式告诉服务器 "image/jpeg"，这样后端就不会报错了
        # -----------------------------------------------------------
        files = {
            "file": (filename, f, "image/jpeg")
        }
        
        response = requests.post(API_URL, files=files)
    
    # 3. 处理结果
    if response.status_code == 200:
        data = response.json()
        print("✅ 服务器返回:", data)
        
        # 提取关键信息
        if data["detections"]:
            best_obj = data["detections"][0]
            print(f"🎯 鉴定结果: 发现了 {best_obj['class']} (置信度: {best_obj['confidence']})")
        else:
            print("💨 没发现啥东西")
    else:
        print(f"❌ 请求失败 (状态码 {response.status_code}):")
        print(response.text)

if __name__ == "__main__":
    # 检查文件是否存在
    if os.path.exists(image_path):
        call_api(image_path)
    else:
        print(f"❌ 找不到图片: {image_path}，请改代码里的路径！")