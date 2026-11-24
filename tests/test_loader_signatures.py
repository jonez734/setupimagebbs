"""Every module the loader runs has init, access, buildargs and main matching bbsengine6's contracts exactly.

The loader matches parameters by position. __main__.main is the console entry point, not a loader module, so it is
excluded.
"""

import importlib
import pkgutil
import unittest

import setupimagebbs
from bbsengine6 import module as be6

STUBS = {
    "init": be6._stub_init,
    "access": be6._stub_access,
    "buildargs": be6._stub_buildargs,
    "main": be6._stub_main,
}
SKIP = {"setupimagebbs.__main__"}


class TestLoaderSignatures(unittest.TestCase):
    def test_every_loader_function_matches_its_contract(self):
        bad = []
        for info in pkgutil.walk_packages(setupimagebbs.__path__, "setupimagebbs."):
            if info.name in SKIP:
                continue
            mod = importlib.import_module(info.name)
            for name, stub in STUBS.items():
                fn = getattr(mod, name, None)
                if not callable(fn):
                    continue
                try:
                    be6.check_signature(fn, stub, name=name)
                except TypeError as exc:
                    bad.append(f"{info.name}.{name}: {exc}")
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
