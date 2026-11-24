import argparse
from bbsengine6 import io, util


def init(args: argparse.Namespace, **kwargs) -> bool | None:
    return True


def access(args: argparse.Namespace, op: str, **kwargs) -> bool | None:
    return True


def buildargs(args: argparse.Namespace, **kwargs) -> argparse.ArgumentParser | None:
    return None


def main(args: argparse.Namespace, **kwargs) -> bool | None:
    setup = kwargs.get("setup", {})
    vice = kwargs.get("vice", {})
    menuitem = kwargs.get("menuitem", None)

    io.echo(f"{setup=} {menuitem=}", level="debug")

    basedir = setup["basedir"] if "basedir" in setup else args.basedir
    basedir = util.inputfilename(args, "basedir: ", basedir, verify=util.verify_dir_exists_writable)
    setup["basedir"] = basedir

    if menuitem is not None:
        menuitem.result = True
        #        menuitem.label = "CHANGED!"
        menuitem.description = "description goes here"
        io.echo(f"setbasedir.120: {menuitem.status=}", level="debug")

    return True
