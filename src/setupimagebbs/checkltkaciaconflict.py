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
    vice = kw["vice"] if "vice" in kw else {}

    bbsengine.util.heading("vice: check for ltk / acia1 conflicts")

    io.echo("check ltk and acia1 conflicts: ", end="")
    if "-aciabase" not in vice or "-ltkio" not in vice:
        io.echo("OK. ltk or acia not defined.")
        return True

    if vice["-acia1base"] == vice["-ltkio"]:
        io.echo(
            "conflict.{f6}acia1base and ltkio are set to the same value (%s)"
            % (vice["-acia1base"]),
            level="error",
        )
        return False
    return True
