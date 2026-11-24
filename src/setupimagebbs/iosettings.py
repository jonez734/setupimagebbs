import argparse
from bbsengine6 import io
import bbsengine6 as bbsengine


def init(args: argparse.Namespace, **kwargs) -> bool | None:
    return True


def access(args: argparse.Namespace, op: str, **kwargs) -> bool | None:
    return True


def buildargs(args: argparse.Namespace, **kwargs) -> argparse.ArgumentParser | None:
    return None


def main(args: argparse.Namespace, **kwargs) -> bool | None:
    bbsengine.util.heading("iocollision handling")
    iocollision = (
        vicecommandline["-iocollision"] if "-iocollision" in vicecommandline else 0
    )

    if iocollision == 0:
        io.echo(
            "{var:currentoptioncolor}[0]{var:labelcolor} error message, detatch all involved carts{/all}"
        )
    else:
        io.echo("[0] error message, detatch all involved carts")

    if iocollision == 1:
        io.echo(
            "{var:currentoptioncolor}[1]{var:labelcolor} error message, detach most recent involved cart{/all}"
        )
    else:
        io.echo("[1] error message, detach most recent involved cart")

    if iocollision == 2:
        io.echo(
            "{var:currentoptioncolor}[2]{var:labelcolor} warning in log, bitwise-and valid return values{/all}"
        )
    else:
        io.echo("[2] warning in log, bitwise-and valid return values")

    ch = io.inputchar(
        "{var:promptcolor}iocollision handling {var:optioncolor}[012]{var:promptcolor}: {var:inputcolor}",
        "012",
        str(iocollision),
    )
    if ch == "0":
        io.echo("0: detach all involved carts")
    elif ch == "1":
        io.echo("1: detach most recent involved cart")
    elif ch == "2":
        io.echo("2: warn, bitwise-and valid return values")
    vicecommandline["-iocollision"] = int(ch)
    return True
