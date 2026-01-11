# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PDF TOC Embedder - A Python tool that parses text-based table of contents files and embeds them as PDF bookmarks/outlines. Uses a plugin-style parser architecture for supporting multiple TOC formats.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default parser (text-indent)
python pdf_toc_embedder.py -i input.pdf -t toc.txt -o output.pdf

# List all available parsers
python pdf_toc_embedder.py --list-parsers

# Run with specific parser
python pdf_toc_embedder.py -i input.pdf -t toc.txt -o output.pdf --parser dash-prefix

# Run with page offset
python pdf_toc_embedder.py -i input.pdf -t toc.txt -o output.pdf --offset 9

# Preview mode (parse without modifying PDF)
python pdf_toc_embedder.py -i input.pdf -t toc.txt -o output.pdf --dry-run
```

## Architecture

### Core Components

**`parsers.py`** - Parser module containing:
- `TocEntry` dataclass: Represents a single TOC entry with `title`, `page`, `level`
- `BaseParser` abstract class: Interface all parsers must implement
- Parser registry: `_PARSERS` dict + `register_parser()`/`get_parser()`/`list_parsers()` functions
- Built-in parsers: `TextIndentParser`, `DashPrefixParser`, `NumberDotParser`

**`pdf_toc_embedder.py`** - Main CLI:
- `get_page_by_number()`: Converts page numbers (1-based) to PDF indices (0-based)
- `add_outline_to_pdf()`: Embeds TOC entries as PDF bookmarks using a stack-based algorithm to handle hierarchical nesting
- `main()`: argparse CLI entry point

### Parser Implementation Pattern

To add a new parser:

1. Create a class inheriting from `BaseParser`
2. Implement three methods:
   - `name(cls) -> str`: Unique parser identifier
   - `description(cls) -> str`: Human-readable description
   - `parse(self, content: str, page_offset: int) -> List[TocEntry]`: Core parsing logic
3. Register via `register_parser(name, ParserClass)`

The `parse()` method receives raw file content and should return `TocEntry` objects. Key considerations:
- Calculate `level` based on your format's hierarchy indicator (indentation, prefix count, etc.)
- Apply `page_offset` to all page numbers: `actual_page = parsed_page + page_offset`
- Skip empty lines; only add entries successfully parsed

### PDF Bookmark Hierarchy Algorithm

The outline construction in `add_outline_to_pdf()` uses a stack to maintain parent relationships:

```
outline_stack = [(bookmark, level), ...]

For each entry:
  1. Pop stack while top.level >= entry.level (find correct parent)
  2. parent = stack.top if exists else None
  3. Create bookmark with parent
  4. Push (bookmark, entry.level) to stack
```

This ensures proper nesting regardless of how levels change (skipping levels, going back multiple levels, etc.).

### Page Offset Logic

The `page_offset` parameter adjusts TOC page numbers to match actual PDF pages. It is applied **once** in the parser's `parse()` method, NOT in `add_outline_to_pdf()`. The `get_page_by_number()` function expects already-offset page numbers and simply converts to 0-based index.

Formula: `actual_pdf_page = toc_page + page_offset`

Example: If TOC says page 1 but it's actually page 10 in PDF, use `--offset 9`.
