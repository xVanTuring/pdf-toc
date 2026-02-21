# 使用 Python 3.13 官方镜像作为基础镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY parsers.py pdf_toc_embedder.py mcp_server.py ./

# 复制 MCP 入口脚本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 创建工作目录
ENV PDF_TOC_WORK_DIR=/data
RUN mkdir -p /data

# 默认运行 PDF TOC 嵌入工具
# 通过 --entrypoint 可以运行 MCP 服务器
ENTRYPOINT ["python", "pdf_toc_embedder.py"]
