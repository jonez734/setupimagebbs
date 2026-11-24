"""setupimagebbs reaches the file helpers through bbsengine6's util module, using the current names.

The camelCase verifiers are deprecated aliases, and bbsengine6 does not export inputfilename or the verifiers at its top
level. Every reference must resolve through util.
"""

import pathlib
import re
import unittest

import bbsengine6
from bbsengine6 import util

SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "setupimagebbs"
TOP_LEVEL_BAD = re.compile(r"\bbsengine\.(verify\w+|inputfilename)|\bbsengine\.(verify\w+|inputfilename)")
DEPRECATED = re.compile(r"\bverify(FileExistsReadable\w*|DirExistsWritable)\b")


class TestVerifyNames(unittest.TestCase):
    def _hits(self, pattern):
        found = []
        for path in SRC.rglob("*.py"):
            if path.name == "_version.py":
                continue
            for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if pattern.search(line) and not line.lstrip().startswith("#"):
                    found.append(f"{path.relative_to(SRC)}:{n}")
        return found

    def test_no_reference_uses_a_top_level_bbsengine_verify_or_inputfilename(self):
        self.assertEqual(self._hits(TOP_LEVEL_BAD), [])

    def test_no_reference_uses_a_deprecated_camelcase_verifier(self):
        self.assertEqual(self._hits(DEPRECATED), [])

    def test_the_current_names_resolve_through_util(self):
        for name in ("inputfilename", "verify_file_exists_readable", "verify_file_exists_readable_writable"):
            self.assertTrue(hasattr(util, name), name)
        self.assertFalse(hasattr(bbsengine6, "inputfilename"))


if __name__ == "__main__":
    unittest.main()
