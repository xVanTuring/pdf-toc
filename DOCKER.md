# PDF TOC Docker 使用指南

## 构建镜像

```bash
docker build -t pdf-toc-embedder .
```

## 方式一：作为 CLI 工具使用

```bash
# 基本用法
docker run --rm -v "$(pwd):/data" pdf-toc-embedder \
  -i /data/input.pdf -t /data/toc.txt -o /data/output.pdf

# 使用页码偏移
docker run --rm -v "$(pwd):/data" pdf-toc-embedder \
  -i /data/input.pdf -t /data/toc.txt -o /data/output.pdf --offset 9

# 列出解析器
docker run --rm pdf-toc-embedder --list-parsers
```

## 方式二：作为 MCP 服务器使用

### 方法 A：通过 Claude Desktop 配置（推荐）

在 `~/.config/Claude/claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "pdf-toc": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "/Users/yourname/Documents/pdf-files:/data",
        "-e", "PDF_TOC_WORK_DIR=/data",
        "pdf-toc-embedder",
        "python", "/app/mcp_server.py"
      ]
    }
  }
}
```

**说明：**
- `/Users/yourname/Documents/pdf-files` 替换为你存放 PDF 文件的目录
- `-i` 参数必须保留，MCP 通过 stdin/stdout 通信
- 容器内路径统一为 `/data`

### 方法 B：直接运行测试

```bash
# 交互式测试（需要在容器内输入 MCP 协议消息）
docker run -it --rm \
  -v "$(pwd):/data" \
  pdf-toc-embedder \
  python /app/mcp_server.py
```

## 文件路径说明

在使用 MCP 服务时，所有路径都相对于挂载的 `/data` 目录：

| 宿主机路径 | 容器内路径（MCP 调用时使用） |
|-----------|------------------------------|
| `/Users/you/docs/book.pdf` | `/data/book.pdf` |
| `/Users/you/docs/toc.txt` | `/data/toc.txt` |

## MCP 工具调用示例

调用 `embed_pdf_toc` 工具时：

```json
{
  "input_pdf": "/data/book.pdf",
  "toc_file": "/data/toc.txt",
  "output_pdf": "/data/book-with-toc.pdf",
  "parser": "text-indent",
  "offset": 0
}
```
