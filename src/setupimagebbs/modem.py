import argparse
from bbsengine6 import io, menu

from . import lib


def init(args: argparse.Namespace, **kwargs) -> bool | None:
    return True


def access(args: argparse.Namespace, op: str, **kwargs) -> bool | None:
    return True


def buildargs(args: argparse.Namespace, **kwargs) -> argparse.ArgumentParser | None:
    return None


def main(args: argparse.Namespace, **kwargs) -> bool | None:
    io.echo("modem{f6}")

    #  menuitem = kw["menuitem"] if "menuitem" in kw else None
    #  setup = kw["setup"] if "setup" in kw else {}

    tcpser = kwargs["tcpser"] if "tcpser" in kwargs else {}

    menuitems = [
        menu.Item("A", "ACIA", "acia"),
        menu.Item("B", "TCPSER", "tcpser"),
        menu.Item(
            "C", "RS232", "rs232", requires=("tcpser",)
        ),  # { "name": "rs232",  "module": "rs232",  "label": "RS232", "requires":("tcpser",)},
    ]
    modemmenu = menu.Menu(args, "modem settings", menuitems)
    done = False
    while not done:
        res = modemmenu.run("modem: ")
        if res.menuitem.key == "X":
            io.echo("exit")
            break

        kwargs["menuitem"] = res.menuitem
        io.echo(f"modem.100: {kwargs=}", level="debug")
        res = lib.runmodule(
            args, res.menuitem.module, **kwargs
        )  # setup=setup, vice=vice, **kw)
        io.echo(f"modem.120: {kwargs=}", level="debug")
