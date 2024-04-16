# 使用一个基础的Python镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY . /app

RUN sed -i 's/http:\/\/deb.debian.org/http:\/\/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources
RUN sed -i 's/http:\/\/security.debian.org/http:\/\/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources

RUN  apt-get -y update &&  apt-get -y upgrade  && apt-get install -y curl && apt-get install -y vim && apt-get install -y gcc && apt-get install -y g++  &&  apt-get install -y default-jdk

# 安装依赖
RUN pip install --upgrade pip && pip install --default-timeout=100 -r requirements.txt -i http://pypi.doubanio.com/simple/ --trusted-host pypi.doubanio.com

# pip install --default-timeout=1000 包名

# 暴露应用的端口
EXPOSE 5000

# 将 app 文件夹为工作目录
WORKDIR /app

# 设置启动命令
# "gunicorn", "-w", "4", "-b", "0.0.0.0:3012", "app:app"
# CMD ["gunicorn", "-c", "gunicorn_config.py", "run:app"]