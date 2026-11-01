"""Core TOC generation logic."""

from __future__ import annotations

import re
from dataclasses import dataclass

FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
TOC_START = "<!-- toc -->"
TOC_END = "<!-- /toc -->"


@dataclass(frozen=True)
class Heading:
    level: int
    text: str
    anchor: str


def slugify(text: str) -> str:
    """Convert heading text to a GitHub-style anchor."""
    slug = text.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug, flags=re.UNICODE)
    slug = re.sub(r"\s+", "-", slug)
    return slug


def parse_headings(markdown: str, include_h1: bool = False) -> list[Heading]:
    """Return headings in document order, ignoring fenced code blocks."""
    headings: list[Heading] = []
    in_fence = False
    seen: dict[str, int] = {}

    for line in markdown.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        match = HEADING_RE.match(line)
        if not match:
            continue

        level = len(match.group(1))
        if level == 1 and not include_h1:
            continue

        text = match.group(2).strip()
        base = slugify(text)
        if base in seen:
            seen[base] += 1
            anchor = f"{base}-{seen[base]}"
        else:
            seen[base] = 0
            anchor = base

        headings.append(Heading(level=level, text=text, anchor=anchor))

    return headings


def render_toc(headings: list[Heading]) -> str:
    """Render headings as a nested Markdown list."""
    if not headings:
        return ""

    lowest = min(h.level for h in headings)
    lines: list[str] = []
    for heading in headings:
        indent = "  " * (heading.level - lowest)
        lines.append(f"{indent}- [{heading.text}](#{heading.anchor})")
    return "\n".join(lines)


def build_toc(markdown: str, include_h1: bool = False) -> str:
    return render_toc(parse_headings(markdown, include_h1=include_h1))


def replace_toc(markdown: str, toc: str) -> str:
    """Replace the region between the marker comments, or append markers."""
    start = markdown.find(TOC_START)
    end = markdown.find(TOC_END)

    block = f"{TOC_START}\n{toc}\n{TOC_END}"

    if start == -1 or end == -1 or end < start:
        separator = "" if markdown.endswith("\n") else "\n"
        return f"{markdown}{separator}\n{block}\n"

    before = markdown[:start]
    after = markdown[end + len(TOC_END):]
    return f"{before}{block}{after}"


def extract_toc(markdown: str) -> str | None:
    """Return the current TOC block content, or None when there is no block."""
    start = markdown.find(TOC_START)
    end = markdown.find(TOC_END)
    if start == -1 or end == -1 or end < start:
        return None
    return markdown[start + len(TOC_START):end].strip()
