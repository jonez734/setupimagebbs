from bbsengine6 import io, menu

from . import lib


def init(args, **kw):
    return True


def access(args, op, **kw):
    return True


def buildargs(args=None, **kw):
    return None


def main(args, **kw):
    io.echo("modem{f6}")

    #  menuitem = kw["menuitem"] if "menuitem" in kw else None
    #  setup = kw["setup"] if "setup" in kw else {}

    tcpser = kw["tcpser"] if "tcpser" in kw else {}

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

        kw["menuitem"] = res.menuitem
        io.echo(f"modem.100: {kw=}", level="debug")
        res = lib.runmodule(
            args, res.menuitem.module, **kw
        )  # setup=setup, vice=vice, **kw)
        io.echo(f"modem.120: {kw=}", level="debug")
