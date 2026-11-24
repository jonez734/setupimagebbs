import subprocess
import argparse

from bbsengine6 import io, util


def init(args: argparse.Namespace, **kwargs) -> bool | None:
    return True


def access(args: argparse.Namespace, op: str, **kwargs) -> bool | None:
    return True


def buildargs(args: argparse.Namespace, **kwargs) -> argparse.ArgumentParser | None:
    return None

def main(args: argparse.Namespace, **kwargs) -> bool | None:
    util.heading("checking for 'tcpser'")
    filename = kwargs.get("filename", "tcpser")
    res = subprocess.run([filename, "-V"], capture_output=True, text=True)

    TCPSERVERSTRING = "(TCPSER) 1.1.6_beta"

    # look for "invalid option -- 'V'" -- (-V added in 1.1.4, older versions will complain of invalid option)
    # ttyio.echo("%r" % (res.stderr))
    # ttyio.echo("stdout=%r" % (res.stdout))
    if (
        res.stdout.find("invalid option -- 'V'") > -1
        or res.stderr.find("invalid option -- 'V'") > -1
    ):
        io.echo(
            "The version of tcpser installed is not compatible with imagebbs (>=1.1.4)."
        )
        return False

    if (
        res.stdout.find(TCPSERVERSTRING) > -1
        or res.stderr.find(TCPSERVERSIONSTRING) > -1
    ):
        io.echo("The version of tcpser installed should be compatible with imagebbs")
        return True
