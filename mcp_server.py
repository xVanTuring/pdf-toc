#!/usr/bin/env python3
"""
PDF TOC MCP Server
提供 PDF 目录操作的 MCP 服务，供 AI 调用
"""

import asyncio
import json
from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from parsers import (
    TocEntry,
    get_parser,
    list_parsers,
    get_default_parser,
)
from pdf_toc_embedder import (
    extract_outline_from_pdf,
    add_outline_to_pdf,
    print_toc_tree,
)

# 创建 MCP 服务器实例
app = Server("pdf-toc-server")


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    列出所有可用的工具
    """
    return [
        Tool(
            name="extract_pdf_toc",
            description="从 PDF 文件中提取目录大纲（书签），返回带层级的目录结构",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "PDF 文件路径"
                    }
                },
                "required": ["pdf_path"]
            }
        ),
        Tool(
            name="embed_pdf_toc",
            description="将目录文本文件嵌入到 PDF 的书签大纲中",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_pdf": {
                        "type": "string",
                        "description": "输入 PDF 文件路径"
                    },
                    "toc_file": {
                        "type": "string",
                        "description": "目录文本文件路径"
                    },
                    "output_pdf": {
                        "type": "string",
                        "description": "输出 PDF 文件路径"
                    },
                    "parser": {
                        "type": "string",
                        "description": "解析器类型 (text-indent, dash-prefix, number-dot)",
                        "enum": ["text-indent", "dash-prefix", "number-dot"],
                        "default": "text-indent"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "页码偏移量",
                        "default": 0
                    }
                },
                "required": ["input_pdf", "toc_file", "output_pdf"]
            }
        ),
        Tool(
            name="list_parsers",
            description="列出所有可用的目录解析器",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="preview_toc_parse",
            description="预览目录文件的解析结果（不修改 PDF）",
            inputSchema={
                "type": "object",
                "properties": {
                    "toc_file": {
                        "type": "string",
                        "description": "目录文本文件路径"
                    },
                    "parser": {
                        "type": "string",
                        "description": "解析器类型 (text-indent, dash-prefix, number-dot)",
                        "enum": ["text-indent", "dash-prefix", "number-dot"],
                        "default": "text-indent"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "页码偏移量",
                        "default": 0
                    }
                },
                "required": ["toc_file"]
            }
        ),
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent | ImageContent | EmbeddedResource]:
    """
    处理工具调用
    """
    try:
        if name == "extract_pdf_toc":
            pdf_path = arguments.get("pdf_path")
            if not pdf_path:
                return [TextContent(type="text", text="错误: 缺少 pdf_path 参数")]

            entries = extract_outline_from_pdf(pdf_path)
            result = {
                "success": True,
                "pdf_path": pdf_path,
                "total_entries": len(entries),
                "entries": [
                    {
                        "title": entry.title,
                        "page": entry.page,
                        "level": entry.level
                    }
                    for entry in entries
                ]
            }
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        elif name == "embed_pdf_toc":
            input_pdf = arguments.get("input_pdf")
            toc_file = arguments.get("toc_file")
            output_pdf = arguments.get("output_pdf")
            parser_name = arguments.get("parser", "text-indent")
            offset = arguments.get("offset", 0)

            if not all([input_pdf, toc_file, output_pdf]):
                return [TextContent(type="text", text="错误: 缺少必需参数 (input_pdf, toc_file, output_pdf)")]

            # 获取解析器
            toc_parser = get_parser(parser_name)
            if not toc_parser:
                return [TextContent(type="text", text=f"错误: 未找到解析器 {parser_name}")]

            # 解析目录文件
            toc_entries = toc_parser.parse_file(toc_file, offset)

            # 添加到 PDF
            add_outline_to_pdf(input_pdf, toc_entries, output_pdf)

            result = {
                "success": True,
                "input_pdf": input_pdf,
                "output_pdf": output_pdf,
                "parser": parser_name,
                "offset": offset,
                "entries_embedded": len(toc_entries)
            }
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        elif name == "list_parsers":
            parsers = list_parsers()
            default_parser = get_default_parser()
            result = {
                "success": True,
                "default_parser": default_parser,
                "parsers": [
                    {"name": name, "description": desc}
                    for name, desc in parsers
                ]
            }
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        elif name == "preview_toc_parse":
            toc_file = arguments.get("toc_file")
            parser_name = arguments.get("parser", "text-indent")
            offset = arguments.get("offset", 0)

            if not toc_file:
                return [TextContent(type="text", text="错误: 缺少 toc_file 参数")]

            # 获取解析器
            toc_parser = get_parser(parser_name)
            if not toc_parser:
                return [TextContent(type="text", text=f"错误: 未找到解析器 {parser_name}")]

            # 解析目录文件
            toc_entries = toc_parser.parse_file(toc_file, offset)

            result = {
                "success": True,
                "toc_file": toc_file,
                "parser": parser_name,
                "offset": offset,
                "total_entries": len(toc_entries),
                "entries": [
                    {
                        "title": entry.title,
                        "page": entry.page,
                        "level": entry.level
                    }
                    for entry in toc_entries
                ]
            }
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        else:
            return [TextContent(type="text", text=f"错误: 未知工具 {name}")]

    except FileNotFoundError as e:
        return [TextContent(type="text", text=f"错误: 文件未找到 - {e}")]
    except Exception as e:
        return [TextContent(type="text", text=f"错误: {e}")]


async def main():
    """启动 MCP 服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pdf-toc-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
