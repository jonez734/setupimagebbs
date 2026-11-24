import argparse
from bbsengine6 import io


def init(args: argparse.Namespace, **kwargs) -> bool | None:
    return True


def access(args: argparse.Namespace, op: str, **kwargs) -> bool | None:
    return True


def buildargs(args: argparse.Namespace, **kwargs) -> argparse.ArgumentParser | None:
    return None


def main(args: argparse.Namespace, **kwargs) -> bool | None:
    io.echo("{var:inputcolor}displaysync{f6}")

    vice = kw["vice"] if "vice" in kw else {}
    menuitem = kw["menuitem"] if "menuitem" in kw else None

    resultbuf = ""

    def ntsc(args, **kwargs):
        vice["-ntsc"] = None
        if "-pal" in vice:
            del vice["-pal"]
        return True

    def pal(args, **kwargs):
        vice["-pal"] = None
        if "-ntsc" in vice:
            del vice["-ntsc"]
        return True

    #  def preprompthook(args):
    #    bbsengine.screen.setarea("vice: display")
    #    return

    #  bbsengine.title("vice: display")
    #  menuitems = [
    #    { "name": "displayntsc", "callback": ntsc, "label": "ntsc", "type":"radiobutton"},
    #    { "name": "displaypal",  "callback": pal,  "label": "pal",  "type":"radiobutton"},
    #  ]
    #  menu = bbsengine.menu.Menu("display", menuitems, args=args)
    #  menu.run("display sync: ", preprompthook)
    #  return (True, resultbuf)

    sync = io.inputchar(
        "{var:optioncolor}[N]{var:promptcolor}TSC or {var:optioncolor}[P]{var:promptcolor}AL? {var:inputcolor}",
        "NP",
        "N",
    )
    if sync == "N":
        io.echo("NTSC")
        vice["-ntsc"] = None
        if "-pal" in vice:
            del vice["-pal"]
        description = "NTSC"
    elif sync == "P":
        io.echo("PAL")
        vice["-pal"] = None
        if "-ntsc" in vice:
            del vice["-ntsc"]
        description = "PAL"
    menuitem.description = description
    menuitem.result = True
    return True
