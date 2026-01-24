import asyncio
import websockets
import json
import datetime

# 这是刚才我们在 main.py 里写的 WebSocket 地址
# 注意协议是 ws:// 而不是 http://
WS_URL = "ws://127.0.0.1:8000/ws"

async def listen_to_server():
    print(f"📱 [虚拟手机] 正在连接服务器: {WS_URL} ...")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ [虚拟手机] 连接成功！等待报警信号...")
            
            while True:
                # 1. 死循环等待，直到服务器发消息过来 (挂起状态，不占CPU)
                message = await websocket.recv()
                
                # 2. 收到消息，解析 JSON
                data = json.loads(message)
                
                # 3. 打印报警信息
                now = datetime.datetime.now().strftime("%H:%M:%S")
                
                if data.get("type") == "detection_alert":
                    print(f"\n🚨 [{now}] 收到报警！！！")
                    print(f"   📦 发现目标: {data['top_object']}")
                    print(f"   📊 置信度:   {data['conf']}")
                    print("-" * 30)
                else:
                    print(f"📩 收到其他消息: {data}")

    except ConnectionRefusedError:
        print("❌ 连接失败：服务器没开吧？去检查一下 uvicorn！")
    except websockets.exceptions.ConnectionClosed:
        print("📴 服务器断开了连接。")
    except Exception as e:
        print(f"💥 出错了: {e}")

if __name__ == "__main__":
    # 启动异步任务
    asyncio.run(listen_to_server())