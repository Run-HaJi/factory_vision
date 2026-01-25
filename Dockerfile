# 1. 选底座
FROM python:3.10-slim

# 2. 设工位
WORKDIR /app

# 3. 装环境 (还是用 Debian 12 的写法，稳)
RUN echo "Types: deb\n\
URIs: http://mirrors.tuna.tsinghua.edu.cn/debian\n\
Suites: bookworm bookworm-updates bookworm-backports\n\
Components: main contrib non-free non-free-firmware\n\
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg\n\
\n\
Types: deb\n\
URIs: http://mirrors.tuna.tsinghua.edu.cn/debian-security\n\
Suites: bookworm-security\n\
Components: main contrib non-free non-free-firmware\n\
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg" > /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 4. 搬清单
COPY requirements.txt .

# 5. 装 Python 库 (🔥 核心修改在这里！)
# 改用阿里源 (mirrors.aliyun.com)
# 增加了 --default-timeout=1000 防止大文件下载超时
# 增加了 --retries=3 给它三次重试机会
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --default-timeout=1000 \
    --retries=3

# 6. 搬代码
COPY . .

# 7. 开窗口
EXPOSE 8000

# 8. 启动令
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]