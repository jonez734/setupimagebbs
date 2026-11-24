"""setbasedir.main: the basedir comes from setup or args, is read with util.inputfilename, and a passed menu item is marked.

A menu item arrives as the ``menuitem`` keyword; it must be the object that gets its result and description set.
"""

import argparse
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from setupimagebbs import setbasedir


class TestSetbasedir(unittest.TestCase):
    def _run(self, *, setup=None, menuitem=None, typed="/new/dir"):
        args = argparse.Namespace(basedir="/default", debug=False)
        with patch.object(setbasedir.util, "inputfilename", return_value=typed) as ask, \
             patch.object(setbasedir.io, "echo"):
            kwargs = {"setup": setup if setup is not None else {}}
            if menuitem is not None:
                kwargs["menuitem"] = menuitem
            result = setbasedir.main(args, **kwargs)
        return result, ask, kwargs

    def test_the_basedir_is_read_with_inputfilename_and_the_verifier(self):
        _, ask, _ = self._run(setup={"basedir": "/from/setup"})
        ask_args, ask_kwargs = ask.call_args
        self.assertEqual(ask_args[2], "/from/setup")
        self.assertIs(ask_kwargs["verify"], setbasedir.util.verify_dir_exists_writable)

    def test_the_typed_basedir_is_stored_in_setup(self):
        setup = {}
        self._run(setup=setup, typed="/new/dir")
        self.assertEqual(setup["basedir"], "/new/dir")

    def test_the_default_comes_from_args_when_setup_has_none(self):
        _, ask, _ = self._run(setup={})
        self.assertEqual(ask.call_args.args[2], "/default")

    def test_a_passed_menu_item_gets_its_result_and_description(self):
        item = SimpleNamespace(status="ok", result=False, description="")
        self._run(menuitem=item)
        self.assertTrue(item.result)
        self.assertEqual(item.description, "description goes here")

    def test_without_a_menu_item_nothing_fails(self):
        result, _, _ = self._run()
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
