"""main() sets up the status line through bbsengine6's bottombar API and accepts the kwargs the module runner passes.

setupimagebbs used the deprecated screen.setbottombar / screen.init / screen.setarea, and lib.setarea took no
**kwargs, so a keyword from the runner raised TypeError in main(). main() now calls bottombar.setbottombar and
bottombar.init. The interactive menu is not run here: it needs a terminal.
"""

import argparse
import importlib
from unittest.mock import patch

main_mod = importlib.import_module("setupimagebbs.main")
lib_mod = importlib.import_module("setupimagebbs.lib")


def _runner_args():
    """The namespace the module runner gives main(): the defaults buildargs registers."""
    return lib_mod.buildargs(argparse.Namespace()).parse_args([])


def _run_main(**kwargs):
    with patch("setupimagebbs.main.util.heading"), \
            patch("setupimagebbs.main.bottombar.setbottombar") as sb, \
            patch("setupimagebbs.main.bottombar.init") as init, \
            patch("setupimagebbs.main.io.getterminalwidth", return_value=80), \
            patch("setupimagebbs.main.locale.setlocale"), \
            patch("setupimagebbs.main.lib.runmodule", return_value=True), \
            patch("setupimagebbs.main.menu.Menu") as menu_cls:
        # The main menu loop exits when the user picks X; return that so main() ends.
        menu_cls.return_value.run.return_value = type("R", (), {"menuitem": type("M", (), {"key": "X"})()})()
        main_mod.main(_runner_args(), **kwargs)
    return sb, init


def test_main_accepts_runner_kwargs_without_error():
    _run_main(player=None)


def test_main_sets_the_bottombar_for_the_app():
    sb, _ = _run_main()
    assert sb.call_args_list[0].args == ("setupimagebbs",)


def test_main_initialises_the_scroll_region_once():
    _, init = _run_main()
    init.assert_called_once()
