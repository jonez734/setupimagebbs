"""The console entry (__main__.main) starts: it builds the argument parser from lib.buildargs and passes the parsed args on.

lib.buildargs takes the loader's args (a required parameter), so main must pass it the args namespace it has, not nothing.
"""

import argparse
import unittest
from unittest.mock import patch

from setupimagebbs import __main__ as entry, lib


class TestStartup(unittest.TestCase):
    def test_buildargs_is_called_with_the_argument_namespace(self):
        parser = lib.buildargs(argparse.Namespace(debug=False))
        self.assertIsInstance(parser, argparse.ArgumentParser)

    def test_main_builds_and_parses_the_arguments_without_error(self):
        with patch.object(entry, "screen"), patch.object(entry, "locale"), patch.object(entry, "time"), \
             patch.object(entry.lib, "init"), patch.object(entry.lib, "runmodule"), \
             patch.object(entry.io, "echo"), \
             patch("sys.argv", ["setupimagebbs"]):
            entry.main()


if __name__ == "__main__":
    unittest.main()
