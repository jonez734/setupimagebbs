import ttyio6 as ttyio
import bbsengine6 as bbsengine


def init(args, **kw):
    return True


def access(args, op, **kw):
    return True


def buildargs(args=None, **kw):
    return None


def main(args, **kwargs):
    bbsengine.util.heading("cmd4000")
    if (
        ttyio.inputboolean(
            "enable cmd fd-4000 on device 9? [{var:engine.currentoptioncolor}Y{/all}n]: ",
            "Y",
            "YN",
        )
        is True
    ):
        vicecommandline["-dos4000"] = bbsengine.inputfilename(
            args,
            "dos4000 filename: ",
            os.path.join(args.basedir, "cmd-fd-4000-dos-v1.40-fd-350022.bin"),
            verify=bbsengine.verifyFileExistsReadable,
        )
        vicecommandline["-drive9type"] = "4000"
        if (
            ttyio.inputboolean(
                "{var:promptcolor}enable drive 9 rtc save? [{var:engine.currentoptioncolor}Y{/all}n]: {var:inputcolor}",
                "Y",
                "YN",
            )
            is True
        ):
            vicecommandline["-drive9rtcsave"] = None
        else:
            vicecommandline["+drive9rtcsave"] = None
