import requests
import os
import csv
import time

# 配置
API_URL = "http://127.0.0.1:8000/predict"
IMAGE_DIR = "datasets/images"     # 图片文件夹路径
REPORT_FILE = "inspection_report.csv" # 结果保存路径

# 支持的图片格式
VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}

def batch_process():
    # 1. 初始化 CSV 文件 (写表头)
    print(f"📄 初始化报表: {REPORT_FILE}")
    with open(REPORT_FILE, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["文件名", "检测结果", "置信度", "耗时(s)", "状态"])

    # 2. 扫描文件夹
    files = [f for f in os.listdir(IMAGE_DIR) if os.path.splitext(f)[1].lower() in VALID_EXTS]
    total = len(files)
    print(f"🔍 扫描到 {total} 张图片，开始批量检测...\n")

    success_count = 0
    
    # 3. 循环处理
    for index, filename in enumerate(files):
        file_path = os.path.join(IMAGE_DIR, filename)
        start_time = time.time()
        
        try:
            # 发送请求
            with open(file_path, "rb") as img_file:
                # 显式指定 MIME 类型
                files = {"file": (filename, img_file, "image/jpeg")}
                response = requests.post(API_URL, files=files)
            
            duration = round(time.time() - start_time, 3)

            # 解析结果
            if response.status_code == 200:
                data = response.json()
                detections = data.get("detections", [])
                
                if detections:
                    # 取置信度最高的一个作为代表
                    top_obj = detections[0]
                    result_str = top_obj['class']
                    conf_str = top_obj['confidence']
                    status = "OK"
                else:
                    result_str = "未检测到"
                    conf_str = 0.0
                    status = "MISS"
                
                success_count += 1
                print(f"[{index+1}/{total}] ✅ {filename} -> {result_str} ({conf_str})")
            else:
                result_str = "Error"
                conf_str = 0.0
                status = f"Fail({response.status_code})"
                print(f"[{index+1}/{total}] ❌ {filename} -> 请求失败")

        except Exception as e:
            duration = 0
            result_str = "Exception"
            conf_str = 0
            status = "ClientError"
            print(f"[{index+1}/{total}] 💥 {filename} -> {e}")

        # 4. 实时写入一行结果 (防止程序中途崩了没保存)
        with open(REPORT_FILE, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([filename, result_str, conf_str, duration, status])

    print(f"\n🏁 处理完成！成功率: {success_count}/{total}")
    print(f"📊 报表已生成: {os.path.abspath(REPORT_FILE)}")

if __name__ == "__main__":
    if os.path.exists(IMAGE_DIR):
        batch_process()
    else:
        print(f"❌ 找不到文件夹: {IMAGE_DIR}")