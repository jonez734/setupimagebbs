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
    bbsengine.util.heading("vice: truedrive")
    vice = kwargs["vice"] if "vice" in kwargs else {}
    if "-truedrive" in vice:
        defaultvalue = "Y"
    elif "+truedrive" in vice:
        defaultvalue = "N"
    else:
        defaultvalue = "Y"

    if defaultvalue == "Y":
        ch = io.inputboolean(
            "{var:promptcolor}truedrive? {var:optioncolor}[{var:currentoptioncolor}Y{var:optioncolor}n]{var:promptcolor}: {var:inputcolor}",
            "Y",
        )
    else:
        ch = io.inputboolean(
            "{var:promptcolor}truedrive? {var:optioncolor}[y{var:currentoptioncolor}N{var:optioncolor}]{var:promptcolor}: {var:inputcolor}",
            "N",
        )

    if ch is True:
        if "+truedrive" in vice:
            del vice["+truedrive"]
        vice["-truedrive"] = None
    else:
        if "-truedrive" in vice:
            del vice["-truedrive"]
        vice["+truedrive"] = None
