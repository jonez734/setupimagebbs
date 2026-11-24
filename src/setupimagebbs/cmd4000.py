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
    bbsengine.util.heading("cmd4000")
    if (
        io.inputboolean(
            "enable cmd fd-4000 on device 9? [{var:engine.currentoptioncolor}Y{/all}n]: ",
            "Y",
            "YN",
        )
        is True
    ):
        vicecommandline["-dos4000"] = bbsengine.util.inputfilename(
            args,
            "dos4000 filename: ",
            os.path.join(args.basedir, "cmd-fd-4000-dos-v1.40-fd-350022.bin"),
            verify=bbsengine.util.verify_file_exists_readable,
        )
        vicecommandline["-drive9type"] = "4000"
        if (
            io.inputboolean(
                "{var:promptcolor}enable drive 9 rtc save? [{var:engine.currentoptioncolor}Y{/all}n]: {var:inputcolor}",
                "Y",
                "YN",
            )
            is True
        ):
            vicecommandline["-drive9rtcsave"] = None
        else:
            vicecommandline["+drive9rtcsave"] = None
