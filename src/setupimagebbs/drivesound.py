import ttyio6 as ttyio
import bbsengine6 as bbsengine


def init(args, **kw):
    return True


def access(args, op, **kw):
    return True


def buildargs(args=None, **kw):
    return None


def main(args, **kwargs):
    #  bbsengine.setarea("vice: drivesound")
    bbsengine.util.heading("vice: drivesound")

    if (
        ttyio.inputboolean(
            "Enable sound emulation of disk drives? [{var:engine.currentoptioncolor}Y{/all}n]: ",
            "Y",
            "YN",
        )
        is True
    ):
        volume = ttyio.inputinteger("drive sound volume? [0-100]: ", 70)
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
