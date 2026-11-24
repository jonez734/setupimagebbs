import argparse
from bbsengine6 import io, util


def init(args: argparse.Namespace, **kwargs) -> bool | None:
    return True


def access(args: argparse.Namespace, op: str, **kwargs) -> bool | None:
    return True


def buildargs(args: argparse.Namespace, **kwargs) -> argparse.ArgumentParser | None:
    return None


def main(args: argparse.Namespace, **kwargs) -> bool | None:
    vice = kwargs["vice"] if "vice" in kwargs else {}
    setup = kwargs["setup"] if "setup" in kwargs else {}
    ioaddrs = setup["ioaddrs"] if "ioaddrs" in kwargs else {}

    tcpser = kwargs["tcpser"] if "tcpser" in kwargs else {}

    util.heading("summary")
    #    lib.setarea("summary")

    #    bbsengine.screen.title("summary")

    if "-default" in vice:
        resetdefaults = True
        del vice["-default"]
    else:
        resetdefaults = False

    for k, v in ioaddrs.items():
        io.echo(f"{k=} {v=}", level="debug")

    opts = []
    buf = ""

    if resetdefaults is True:
        opts.append("-default")

    for k, v in vice.items():
        if v is not None:
            buf = f"{k} {v}"
        else:
            buf = f"{k}"

        opts.append(buf)

    io.echo("x64sc %s" % (" \\{f6} ".join(opts)), wordwrap=False)

    opts = []

    for k, v in tcpser.items():
        if v is not None:
            buf = "%s %s" % (k, v)
        else:
            buf = "%s" % (k)

        opts.append(buf)

    io.echo("tcpser %s" % (" ".join(opts)))

    return True
