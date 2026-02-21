#!/bin/bash
# PDF TOC MCP 服务器启动脚本
# 用于在 Claude Desktop 中配置 MCP 服务

set -e

# 默认工作目录（可在配置中覆盖）
WORK_DIR="${PDF_TOC_WORK_DIR:-/data}"

echo "Starting PDF TOC MCP Server..." >&2
echo "Working directory: $WORK_DIR" >&2

# 确保工作目录存在
mkdir -p "$WORK_DIR"

cd "$WORK_DIR"

# 启动 MCP 服务器
exec python /app/mcp_server.py
