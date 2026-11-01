import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from markdown_toc.__main__ import main


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class CliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_print_mode(self):
        doc = self.tmp / "README.md"
        doc.write_text("## Install\n## Usage\n", encoding="utf-8")
        code, out, _ = run([str(doc)])
        self.assertEqual(code, 0)
        self.assertIn("- [Install](#install)", out)

    def test_write_mode_creates_markers(self):
        doc = self.tmp / "README.md"
        doc.write_text("## Install\n", encoding="utf-8")
        self.assertEqual(run([str(doc), "--write"])[0], 0)
        content = doc.read_text(encoding="utf-8")
        self.assertIn("<!-- toc -->", content)
        self.assertIn("- [Install](#install)", content)

    def test_check_fails_when_stale(self):
        doc = self.tmp / "README.md"
        doc.write_text("## Install\n", encoding="utf-8")
        run([str(doc), "--write"])
        doc.write_text(doc.read_text(encoding="utf-8") + "## New\n", encoding="utf-8")
        self.assertEqual(run([str(doc), "--check"])[0], 1)

    def test_check_passes_when_current(self):
        doc = self.tmp / "README.md"
        doc.write_text("## Install\n", encoding="utf-8")
        run([str(doc), "--write"])
        self.assertEqual(run([str(doc), "--check"])[0], 0)

    def test_check_without_markers(self):
        doc = self.tmp / "README.md"
        doc.write_text("## Install\n", encoding="utf-8")
        self.assertEqual(run([str(doc), "--check"])[0], 1)

    def test_missing_file_returns_2(self):
        self.assertEqual(run([str(self.tmp / "nope.md")])[0], 2)


if __name__ == "__main__":
    unittest.main()
