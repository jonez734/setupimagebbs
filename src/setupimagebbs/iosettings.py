import ttyio6 as ttyio
import bbsengine6 as bbsengine


def init(args, **kw):
    return True


def access(args, op, **kw):
    return True


def buildargs(args=None, **kw):
    return None


def main(args, **kwargs):
    bbsengine.util.heading("iocollision handling")
    iocollision = (
        vicecommandline["-iocollision"] if "-iocollision" in vicecommandline else 0
    )

    if iocollision == 0:
        ttyio.echo(
            "{var:currentoptioncolor}[0]{var:labelcolor} error message, detatch all involved carts{/all}"
        )
    else:
        ttyio.echo("[0] error message, detatch all involved carts")

    if iocollision == 1:
        ttyio.echo(
            "{var:currentoptioncolor}[1]{var:labelcolor} error message, detach most recent involved cart{/all}"
        )
    else:
        ttyio.echo("[1] error message, detach most recent involved cart")

    if iocollision == 2:
        ttyio.echo(
            "{var:currentoptioncolor}[2]{var:labelcolor} warning in log, bitwise-and valid return values{/all}"
        )
    else:
        ttyio.echo("[2] warning in log, bitwise-and valid return values")

    ch = ttyio.inputchar(
        "{var:promptcolor}iocollision handling {var:optioncolor}[012]{var:promptcolor}: {var:inputcolor}",
        "012",
        str(iocollision),
    )
    if ch == "0":
        ttyio.echo("0: detach all involved carts")
    elif ch == "1":
        ttyio.echo("1: detach most recent involved cart")
    elif ch == "2":
        ttyio.echo("2: warn, bitwise-and valid return values")
    vicecommandline["-iocollision"] = int(ch)
    return True
