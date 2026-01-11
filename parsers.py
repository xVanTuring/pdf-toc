#!/usr/bin/env python3
"""
TOC解析器模块
支持多种目录格式的解析器
"""

import re
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class TocEntry:
    """目录条目类"""
    title: str
    page: int
    level: int

    def __repr__(self):
        indent = "  " * self.level
        return f"{indent}- {self.title} / {self.page}"


class BaseParser(ABC):
    """TOC解析器基类"""

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """返回解析器名称"""
        pass

    @classmethod
    @abstractmethod
    def description(cls) -> str:
        """返回解析器描述"""
        pass

    @abstractmethod
    def parse(self, content: str, page_offset: int = 0) -> List[TocEntry]:
        """
        解析目录内容

        Args:
            content: 目录文件内容
            page_offset: 页码偏移量

        Returns:
            目录条目列表
        """
        pass

    def parse_file(self, file_path: str, page_offset: int = 0) -> List[TocEntry]:
        """
        解析目录文件

        Args:
            file_path: 目录文件路径
            page_offset: 页码偏移量

        Returns:
            目录条目列表
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.parse(content, page_offset)


class TextIndentParser(BaseParser):
    """
    文本缩进格式解析器

    格式说明：
    - 使用 '- ' 前缀表示条目
    - 缩进（每2个空格一级）表示层级
    - 页码格式: 标题 / 页码

    示例:
    - 导论 / 1
      - 一、什么是马克思主义/ 2
      - 二、马克思主义的创立与发展/ 4
    - 第一章 世界的物质性及发展规律/ 25
    """

    @classmethod
    def name(cls) -> str:
        return "text-indent"

    @classmethod
    def description(cls) -> str:
        return "文本缩进格式 (每2空格一级, 格式: - 标题 / 页码)"

    def parse(self, content: str, page_offset: int = 0) -> List[TocEntry]:
        entries = []

        for line in content.splitlines():
            line = line.rstrip('\n')
            if not line.strip():
                continue

            # 计算前导空格数（每2个空格一级）
            leading_spaces = len(line) - len(line.lstrip(' '))
            level = leading_spaces // 2

            # 移除前导空格和'-'
            content_line = line.lstrip()
            while content_line.startswith('-'):
                content_line = content_line[1:].lstrip()

            # 解析标题和页码
            page_match = re.search(r'/\s*(\d+)', content_line)
            if page_match:
                page = int(page_match.group(1)) + page_offset
                title = content_line[:page_match.start()].strip()
                entries.append(TocEntry(title, page, level))

        return entries


class DashPrefixParser(BaseParser):
    """
    连字符前缀格式解析器

    格式说明：
    - 使用连续的 '-' 数量表示层级
    - 页码格式: 标题 / 页码

    示例:
    - 导论 / 1
    -- 一、什么是马克思主义/ 2
    -- 二、马克思主义的创立与发展/ 4
    --- (一)马克思主义的创立/ 4
    ---- 1.产生的经济社会根源/ 4
    """

    @classmethod
    def name(cls) -> str:
        return "dash-prefix"

    @classmethod
    def description(cls) -> str:
        return "连字符前缀格式 (连续'-'数量表示层级)"

    def parse(self, content: str, page_offset: int = 0) -> List[TocEntry]:
        entries = []

        for line in content.splitlines():
            line = line.rstrip('\n')
            if not line.strip():
                continue

            # 计算前导'-'数量
            stripped = line.lstrip()
            dash_count = len(line) - len(stripped)
            level = 0
            temp = stripped
            while temp.startswith('-'):
                temp = temp[1:].lstrip()
                level += 1

            # 解析标题和页码
            page_match = re.search(r'/\s*(\d+)', temp)
            if page_match:
                page = int(page_match.group(1)) + page_offset
                title = temp[:page_match.start()].strip()
                entries.append(TocEntry(title, page, level))

        return entries


class NumberDotParser(BaseParser):
    """
    数字点号格式解析器

    格式说明：
    - 使用 "1." "1.1" 等表示层级
    - 页码格式: 标题.......页码 或 标题 页码

    示例:
    1. 导论...................................1
    1.1 什么是马克思主义........................2
    1.2 马克思主义的创立与发展..................4
    """

    @classmethod
    def name(cls) -> str:
        return "number-dot"

    @classmethod
    def description(cls) -> str:
        return "数字点号格式 (1. 1.1 等表示层级)"

    def parse(self, content: str, page_offset: int = 0) -> List[TocEntry]:
        entries = []

        for line in content.splitlines():
            line = line.rstrip('\n')
            if not line.strip():
                continue

            # 计算层级（根据数字点号数量）
            level = 0
            temp = line.strip()
            pattern = r'^(\d+\.)+'

            match = re.match(pattern, temp)
            if match:
                prefix = match.group(1)
                level = prefix.count('.')
                temp = temp[len(prefix):].strip()
            else:
                # 无数字前缀，作为顶级
                level = 0

            # 解析页码（查找行末的数字）
            page_match = re.search(r'(\d+)\s*$', temp)
            if page_match:
                page = int(page_match.group(1)) + page_offset
                title = temp[:page_match.start()].strip()
                # 移除可能的点号分隔符
                title = re.sub(r'^\.+\.+', '', title)
                title = re.sub(r'\.+$', '', title)
                entries.append(TocEntry(title, page, level))

        return entries


# 解析器注册表
_PARSERS: dict[str, type[BaseParser]] = {
    'text-indent': TextIndentParser,
    'dash-prefix': DashPrefixParser,
    'number-dot': NumberDotParser,
}


def register_parser(name: str, parser_class: type[BaseParser]) -> None:
    """注册新的解析器"""
    _PARSERS[name] = parser_class


def get_parser(name: str) -> Optional[BaseParser]:
    """获取指定名称的解析器实例"""
    parser_class = _PARSERS.get(name)
    if parser_class:
        return parser_class()
    return None


def list_parsers() -> List[tuple[str, str]]:
    """列出所有可用解析器"""
    return [(name, cls.description()) for name, cls in _PARSERS.items()]


def get_default_parser() -> str:
    """获取默认解析器名称"""
    return 'text-indent'
