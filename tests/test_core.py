import unittest

from markdown_toc.core import (
    build_toc,
    extract_toc,
    headings_to_json,
    parse_headings,
    render_toc,
    replace_toc,
    slugify,
)


class SlugifyTests(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_strips_punctuation(self):
        self.assertEqual(slugify("What's new?"), "whats-new")

    def test_keeps_hyphens(self):
        self.assertEqual(slugify("well-known tools"), "well-known-tools")

    def test_handles_unicode_words(self):
        self.assertEqual(slugify("Café Menu"), "café-menu")


class ParseHeadingTests(unittest.TestCase):
    def test_levels(self):
        headings = parse_headings("# Title\n## One\n### Two\n")
        self.assertEqual([h.level for h in headings], [2, 3])
        self.assertEqual([h.text for h in headings], ["One", "Two"])

    def test_can_include_h1(self):
        headings = parse_headings("# Title\n## One\n", include_h1=True)
        self.assertEqual([h.level for h in headings], [1, 2])

    def test_ignores_backtick_fence(self):
        md = "## Real\n```bash\n# not a heading\n```\n## Also real\n"
        self.assertEqual([h.text for h in parse_headings(md)], ["Real", "Also real"])

    def test_ignores_tilde_fence(self):
        md = "## Real\n~~~\n## fake\n~~~\n"
        self.assertEqual([h.text for h in parse_headings(md)], ["Real"])

    def test_duplicates_get_suffixes(self):
        md = "## Setup\n## Setup\n## Setup\n"
        self.assertEqual(
            [h.anchor for h in parse_headings(md)],
            ["setup", "setup-1", "setup-2"],
        )

    def test_no_headings(self):
        self.assertEqual(parse_headings("just text\n"), [])


class RenderTests(unittest.TestCase):
    def test_indentation(self):
        self.assertEqual(
            build_toc("## A\n### B\n## C\n"),
            "- [A](#a)\n  - [B](#b)\n- [C](#c)",
        )

    def test_empty(self):
        self.assertEqual(render_toc([]), "")


class ReplaceTocTests(unittest.TestCase):
    def test_appends_markers_when_missing(self):
        out = replace_toc("# Doc\n\n## A\n", "- [A](#a)")
        self.assertIn("<!-- toc -->", out)
        self.assertIn("<!-- /toc -->", out)
        self.assertTrue(out.rstrip().endswith("<!-- /toc -->"))

    def test_replaces_existing_block(self):
        md = "## A\n\n<!-- toc -->\nOLD\n<!-- /toc -->\n\ntail\n"
        out = replace_toc(md, "- [A](#a)")
        self.assertNotIn("OLD", out)
        self.assertIn("- [A](#a)", out)
        self.assertIn("tail", out)


class ExtractTocTests(unittest.TestCase):
    def test_none_without_markers(self):
        self.assertIsNone(extract_toc("## A\n"))

    def test_returns_content(self):
        md = "<!-- toc -->\n- [A](#a)\n<!-- /toc -->\n"
        self.assertEqual(extract_toc(md), "- [A](#a)")


class HeadingsToJsonTests(unittest.TestCase):
    def test_returns_json_list(self):
        import json

        md = "## Install\n### From source\n"
        data = json.loads(headings_to_json(md))
        self.assertEqual(
            data,
            [
                {"level": 2, "text": "Install", "anchor": "install"},
                {"level": 3, "text": "From source", "anchor": "from-source"},
            ],
        )

    def test_respects_include_h1(self):
        import json

        data = json.loads(headings_to_json("# Title\n", include_h1=True))
        self.assertEqual(data[0]["level"], 1)


if __name__ == "__main__":
    unittest.main()
