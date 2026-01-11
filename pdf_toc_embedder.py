#!/usr/bin/env python3
"""
PDF目录嵌入工具
解析目录文本文件并将目录嵌入到指定PDF中
"""

import argparse
from typing import List

from parsers import (
    TocEntry,
    BaseParser,
    get_parser,
    list_parsers,
    get_default_parser,
    register_parser
)


def get_page_by_number(reader, page_num: int) -> int:
    """
    获取PDF中指定页码的索引

    Args:
        reader: PDF阅读器
        page_num: 页码（从1开始）

    Returns:
        页面索引（从0开始）
    """
    if page_num < 1 or page_num > len(reader.pages):
        return len(reader.pages) - 1  # 返回最后一页作为fallback
    return page_num - 1


def add_outline_to_pdf(pdf_path: str, toc_entries: List[TocEntry],
                       output_path: str) -> None:
    """
    将目录添加到PDF的大纲中

    Args:
        pdf_path: 输入PDF文件路径
        toc_entries: 目录条目列表
        output_path: 输出PDF文件路径
    """
    from PyPDF2 import PdfReader, PdfWriter

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # 复制所有页面
    for page in reader.pages:
        writer.add_page(page)

    # 构建大纲树结构
    outline_stack = []  # (bookmark, level)

    for entry in toc_entries:
        # 获取目标页面索引
        page_index = get_page_by_number(reader, entry.page)

        # 根据层级找到父节点
        while outline_stack and outline_stack[-1][1] >= entry.level:
            outline_stack.pop()

        # 确定父节点
        parent = outline_stack[-1][0] if outline_stack else None

        # 创建书签
        bookmark = writer.add_outline_item(
            entry.title,
            page_index,
            parent=parent
        )

        # 将当前书签压入栈
        outline_stack.append((bookmark, entry.level))

    # 写入输出文件
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)


def print_toc_tree(toc_entries: List[TocEntry]) -> None:
    """打印目录树结构"""
    print("目录结构:")
    print("=" * 50)
    for entry in toc_entries:
        print(entry)
    print("=" * 50)
    print(f"共 {len(toc_entries)} 个条目")


def main():
    parser = argparse.ArgumentParser(
        description='将目录嵌入到PDF文件中',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -i input.pdf -t toc.txt -o output.pdf
  %(prog)s -i input.pdf -t toc.txt -o output.pdf --offset 5
  %(prog)s -i input.pdf -t toc.txt -o output.pdf --parser dash-prefix
  %(prog)s --list-parsers
        """
    )

    parser.add_argument('-i', '--input',
                        help='输入PDF文件路径')
    parser.add_argument('-t', '--toc',
                        help='目录文本文件路径')
    parser.add_argument('-o', '--output',
                        help='输出PDF文件路径')
    parser.add_argument('--offset', type=int, default=0,
                        help='页码偏移量 (默认: 0)')
    parser.add_argument('-p', '--parser', default=get_default_parser(),
                        help='解析器类型 (默认: text-indent)')
    parser.add_argument('--list-parsers', action='store_true',
                        help='列出所有可用解析器')
    parser.add_argument('--dry-run', action='store_true',
                        help='只显示解析的目录，不修改PDF')

    args = parser.parse_args()

    # 列出解析器
    if args.list_parsers:
        print("可用解析器:")
        for name, desc in list_parsers():
            default = " (默认)" if name == get_default_parser() else ""
            print(f"  {name}{default:12} - {desc}")
        return

    # 检查必需参数
    if not all([args.input, args.toc, args.output]):
        parser.error("需要 -i, -t, -o 参数")

    # 获取解析器
    toc_parser = get_parser(args.parser)
    if not toc_parser:
        parser.error(f"未找到解析器: {args.parser}")

    # 解析目录文件
    print(f"正在解析目录文件: {args.toc}")
    print(f"使用解析器: {args.parser}")
    toc_entries = toc_parser.parse_file(args.toc, args.offset)

    # 显示目录结构
    print_toc_tree(toc_entries)

    if args.dry_run:
        print("\n[预览模式] 未修改PDF文件")
        return

    # 添加到PDF
    print(f"\n正在处理PDF: {args.input}")
    print(f"页码偏移量: {args.offset}")

    try:
        add_outline_to_pdf(args.input, toc_entries, args.output)
        print(f"成功! 输出文件: {args.output}")
    except FileNotFoundError:
        print(f"错误: 找不到文件 {args.input}")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == '__main__':
    main()
