import argparse
from bbsengine6 import io


def init(args: argparse.Namespace, **kwargs) -> bool | None:
    return True


def access(args: argparse.Namespace, op: str, **kwargs) -> bool | None:
    return True


def buildargs(args: argparse.Namespace, **kwargs) -> argparse.ArgumentParser | None:
    return None


def main(args: argparse.Namespace, **kwargs) -> bool | None:
    vice = kw["vice"] if "vice" in kw else {}
    menuitem = kw["menuitem"] if "menuitem" in kw else None
    io.echo(f"{menuitem=}", level="debug")

    #  bbsengine.screen.setarea("vice: confirm before exit")

    if "-confirmonexit" in vice:
        confirmonexit = "Y"
    elif "+confirmonexit" in vice:
        confirmonexit = "N"
    else:
        confirmonexit = "Y"

    prompt = "{var:promptcolor}confirm before vice exit? ["
    if confirmonexit == "Y":
        prompt += "{var:currentoptioncolor}Y{var:optioncolor}n"
    else:
        prompt += "{var:optioncolor}y{var:currentoptioncolor}N"
    prompt += "{var:optioncolor}]{var:promptcolor}: {var:inputcolor}"
    if io.inputboolean(prompt, confirmonexit) is True:
        vice["-confirmonexit"] = None
        if "+confirmonexit" in vice:
            del vice["+confirmonexit"]
        status = "Yes"
    else:
        vice["+confirmonexit"] = None
        if "-confirmonexit" in vice:
            del vice["-confirmonexit"]
        status = "No"

    if menuitem is not None:
        menuitem.description = status
    return True
