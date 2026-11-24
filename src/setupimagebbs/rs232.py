import argparse
from bbsengine6 import io, util


def init(args: argparse.Namespace, **kwargs) -> bool | None:
    return True


def access(args: argparse.Namespace, op: str, **kwargs) -> bool | None:
    return True


def buildargs(args: argparse.Namespace, **kwargs) -> argparse.ArgumentParser | None:
    return None


def main(args: argparse.Namespace, **kwargs) -> bool | None:
    io.echo("rs232")

    menuitem = kw["menuitem"] if "menuitem" in kw else None
    tcpser = kw["tcpser"] if "tcpser" in kw else {}
    vice = kw["vice"] if "vice" in kw else {}
    setup = kw["setup"] if "setup" in kw else {}
    localhost = setup["localhost"] if "localhost" in setup else None

    util.heading("vice: rs232/ip232")

    dev = io.inputinteger(
        "{var:promptcolor}device {var:optioncolor}[1-4]{var:promptcolor}: {var:inputcolor}",
        4,
    )
    vice["+rsuser"] = None
    vice["-rsdev%d" % (dev)] = "%s:%s" % (localhost, tcpser["-v"])
    ip232 = io.inputboolean(
        "{var:promptcolor}enable ip232? {var:optioncolor}[Yn]{var:promptcolor}: ", "Y"
    )
    vice["-rsdev%dip232" % (dev)] = ip232
    baud = io.inputinteger(
        "{var:promptcolor}baud rate: {var:inputcolor}", tcpser["-s"]
    )  # 38400
    vice["-rsdev%dbaud" % (dev)] = baud

    if menuitem is not None:
        menuitem.result = True
        menuitem.description = f"[dev: {dev}] [ip232: {ip232}] [baud: {baud}]"
    return True
