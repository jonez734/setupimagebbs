import argparse
from bbsengine6 import io
def init(args: argparse.Namespace, **kwargs) -> bool | None:
    return True


def buildargs(args: argparse.Namespace, **kwargs) -> argparse.ArgumentParser | None:
    return None


def access(args: argparse.Namespace, op: str, **kwargs) -> bool | None:
    return True


def main(args: argparse.Namespace, **kwargs) -> bool | None:
    #  bbsengine.setarea("vice: keyboard")
    bbsengine.util.heading("keyboard")

    keyboards = (
        "0: Symbpolic",
        "1: Positional",
        "2: symbolic (user)",
        "3: positional (user)",
    )
    ch = io.inputchar(
        "Specify index of keymap file ({var:engine.currentoptioncolor}0:symbolic{/all}, 1:positional, 2:symbolic (user), 3:positional (user))? [0123]: ",
        "0123",
        "0",
    )
    if ch == "0":
        resultbuf = "symbolic"
    elif ch == "1":
        resultbuf = "positional"
    elif ch == "2":
        resultbuf = "symbolic (user)"
    elif ch == "3":
        resultbuf = "positional (user)"
    else:
        resultbuf = ""

    vicecommandline["-keymap"] = ch
    return (True, resultbuf)
