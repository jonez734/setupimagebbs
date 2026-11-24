"""The packaged setupimagebbs code runs on bbsengine6, not the retired ttyio package.

Every module in the package must import, and none may refer to ttyio, bbsengine5 or ttyio5. The status join in clock.py
keeps its plain "a, b and c" form.
"""

import importlib
import pkgutil
import re
import pathlib
import unittest

import setupimagebbs

PKG = pathlib.Path(setupimagebbs.__file__).parent


class TestPackage(unittest.TestCase):
    def test_every_module_imports(self):
        failed = []
        for mod in pkgutil.walk_packages(setupimagebbs.__path__, "setupimagebbs."):
            try:
                importlib.import_module(mod.name)
            except Exception as exc:  # report every failure, not the first
                failed.append((mod.name, type(exc).__name__, str(exc)[:80]))
        self.assertEqual(failed, [])

    def test_no_module_refers_to_ttyio_or_bbsengine5(self):
        pattern = re.compile(r"\bttyio\d*\b|\bbbsengine5\b|\bbsengine5\b")
        hits = []
        for path in PKG.rglob("*.py"):
            if path.name == "_version.py":
                continue
            for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if pattern.search(line) and not line.lstrip().startswith("#"):
                    hits.append(f"{path.relative_to(PKG)}:{n}")
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
