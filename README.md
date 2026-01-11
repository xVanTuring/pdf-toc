# PDF目录嵌入工具

将文本格式的目录嵌入到PDF文件的书签大纲中，支持多种目录格式。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python pdf_toc_embedder.py -i input.pdf -t toc.txt -o output.pdf
```

### 查看可用解析器

```bash
python pdf_toc_embedder.py --list-parsers
```

### 指定解析器

```bash
python pdf_toc_embedder.py -i input.pdf -t toc.txt -o output.pdf --parser dash-prefix
```

### 带页码偏移

```bash
python pdf_toc_embedder.py -i input.pdf -t toc.txt -o output.pdf --offset 5
```

### 预览模式

```bash
python pdf_toc_embedder.py -i input.pdf -t toc.txt -o output.pdf --dry-run
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `-i, --input` | 输入PDF文件路径 |
| `-t, --toc` | 目录文本文件路径 |
| `-o, --output` | 输出PDF文件路径 |
| `--offset` | 页码偏移量（默认: 0） |
| `-p, --parser` | 解析器类型（默认: text-indent） |
| `--list-parsers` | 列出所有可用解析器 |
| `--dry-run` | 预览模式，只显示解析结果 |

## 内置解析器

### text-indent（默认）

文本缩进格式，每2个空格一级：

```
- 导论 / 1
  - 一、什么是马克思主义/ 2
  - 二、马克思主义的创立与发展/ 4
- 第一章 世界的物质性及发展规律/ 25
  - 第一节 世界的多样性与物质统一性/ 26
```

### dash-prefix

连字符前缀格式，连续`-`数量表示层级：

```
- 导论 / 1
-- 一、什么是马克思主义/ 2
--- (一)马克思主义的创立/ 4
---- 1.产生的经济社会根源/ 4
```

### number-dot

数字点号格式：

```
1. 导论...................................1
1.1 什么是马克思主义........................2
1.2 马克思主义的创立与发展..................4
```

## 自定义解析器

创建自定义解析器，继承`BaseParser`类：

```python
from parsers import BaseParser, TocEntry, register_parser
import re
from typing import List

class MyParser(BaseParser):
    @classmethod
    def name(cls) -> str:
        return "my-parser"

    @classmethod
    def description(cls) -> str:
        return "我的解析器描述"

    def parse(self, content: str, page_offset: int = 0) -> List[TocEntry]:
        entries = []
        # 你的解析逻辑
        return entries

# 注册解析器
register_parser("my-parser", MyParser)
```

参考 `custom_parser_example.py` 查看完整示例。
