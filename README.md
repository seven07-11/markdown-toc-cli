# markdown-toc-cli

A tiny command-line tool that generates and verifies a table of contents for Markdown files.
Pure Python, standard library only.

## Why

Long README files are hard to navigate. This tool builds a nested TOC from the headings
you already wrote, and can check in CI that the committed TOC has not gone stale.

## Install

```bash
pip install .
```

Or run it straight from the source tree:

```bash
python -m markdown_toc README.md
```

## Usage

```bash
# Print a TOC for a file
markdown-toc README.md

# Write it into the file between the marker comments
markdown-toc README.md --write

# Fail (exit 1) if the TOC in the file is out of date — useful in CI
markdown-toc README.md --check
```

### Marker comments

`--write` replaces whatever sits between these two lines:

```markdown
<!-- toc -->
- [Why](#why)
- [Install](#install)
- [Usage](#usage)
  - [Marker comments](#marker-comments)
- [Example](#example)
- [Behaviour details](#behaviour-details)
- [Development](#development)
- [License](#license)
<!-- /toc -->
```

If the markers are missing they are appended at the end of the file.

## Example

Input:

```markdown
# Project
## Install
### From source
## Usage
```

Output:

```markdown
- [Project](#project)
  - [Install](#install)
    - [From source](#from-source)
  - [Usage](#usage)
```

## Behaviour details

- Headings inside fenced code blocks are ignored (both ``` and `~~~` fences).
- The document's own `# Title` is skipped by default; pass `--include-h1` to keep it.
- Anchors follow the GitHub slug rules: lowercase, punctuation dropped, spaces to hyphens.
- Duplicate headings get `-1`, `-2` suffixes, matching GitHub's behaviour.

## Development

Tests use the standard library, so no dependencies are required:

```bash
python -m unittest discover -s tests -v
```

`pytest` also picks them up if you prefer it.

## License

MIT
