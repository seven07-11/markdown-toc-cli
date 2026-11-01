"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import build_toc, extract_toc, replace_toc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="markdown-toc",
        description="Generate a table of contents for a Markdown file.",
    )
    parser.add_argument("path", type=Path, help="Markdown file to process")
    parser.add_argument(
        "--write",
        action="store_true",
        help="write the TOC into the file between the marker comments",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 when the TOC in the file is out of date",
    )
    parser.add_argument(
        "--include-h1",
        action="store_true",
        help="include the document's top-level heading",
    )
    args = parser.parse_args(argv)

    try:
        markdown = args.path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"markdown-toc: {args.path}: {error}", file=sys.stderr)
        return 2

    toc = build_toc(markdown, include_h1=args.include_h1)

    if args.check:
        current = extract_toc(markdown)
        if current is None:
            print(f"markdown-toc: {args.path}: no TOC markers found", file=sys.stderr)
            return 1
        if current != toc.strip():
            print(f"markdown-toc: {args.path}: TOC is out of date", file=sys.stderr)
            return 1
        print(f"markdown-toc: {args.path}: TOC is up to date")
        return 0

    if args.write:
        updated = replace_toc(markdown, toc)
        args.path.write_text(updated, encoding="utf-8")
        print(f"markdown-toc: wrote TOC to {args.path}")
        return 0

    print(toc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
