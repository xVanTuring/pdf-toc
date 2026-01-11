#!/usr/bin/env python3
"""
自定义解析器示例

展示如何创建并注册自定义解析器
"""

from parsers import BaseParser, TocEntry, register_parser
import re
from typing import List


class MyCustomParser(BaseParser):
    """
    自定义解析器示例

    格式说明:
    - 根据你的需求定义格式
    """

    @classmethod
    def name(cls) -> str:
        return "my-custom"

    @classmethod
    def description(cls) -> str:
        return "我的自定义解析器 - 描述你的格式"

    def parse(self, content: str, page_offset: int = 0) -> List[TocEntry]:
        entries = []

        for line in content.splitlines():
            line = line.rstrip('\n')
            if not line.strip():
                continue

            # ===== 在这里编写你的解析逻辑 =====

            # 示例: 解析层级
            level = 0  # 根据你的格式计算层级

            # 示例: 解析标题和页码
            # 使用正则表达式或其他方法提取
            title = "示例标题"
            page = 1 + page_offset

            # 只有成功解析时才添加
            entries.append(TocEntry(title, page, level))

        return entries


# 注册解析器
register_parser("my-custom", MyCustomParser)


# 使用示例:
# python pdf_toc_embedder.py -i input.pdf -t toc.txt -o output.pdf --parser my-custom
