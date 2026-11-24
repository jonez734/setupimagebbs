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
    #  bbsengine.setarea("vice: drivesound")
    bbsengine.util.heading("vice: drivesound")

    if (
        io.inputboolean(
            "Enable sound emulation of disk drives? [{var:engine.currentoptioncolor}Y{/all}n]: ",
            "Y",
            "YN",
        )
        is True
    ):
        volume = io.inputinteger("drive sound volume? [0-100]: ", 70)
        if "+drivesound" in vicecommandline:
            del vicecommandline["+drivesound"]
        vicecommandline["-drivesound"] = None
        vicecommandline["-drivesoundvolume"] = volume
    else:
        if "-drivesound" in vicecommandline:
            del vicecommandline["-drivesound"]
        if "-drivesoundvolume" in vicecommandline:
            del vicecommandline["-drivesoundvolume"]
        vicecommandline["+drivesound"] = None
    resultbuf = "(disabled)"
    if "-drivesound" in vicecommandline:
        return (True, "enabled: vol=%s" % (vicecommandline["-drivesoundvolume"]))
    return (True, resultbuf)
