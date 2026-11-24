import argparse
from bbsengine6 import io, util, input


def init(args: argparse.Namespace, **kwargs) -> bool | None:
    return True


def access(args: argparse.Namespace, op: str, **kwargs) -> bool | None:
    return True


def buildargs(args: argparse.Namespace, **kwargs) -> argparse.ArgumentParser | None:
    return None


def main(args: argparse.Namespace, **kwargs) -> bool | None:
    setup = kw["setup"] if "setup" in kw else {}
    vice = kw["vice"] if "vice" in kw else {}
    mi = kw["menuitem"] if "menuitem" in kw else None

    io.echo(f"{setup=}")

    #    ttyio.echo(f"setbasedir.100: {mi=}", level="debug")

    basedir = setup["basedir"] if "basedir" in setup else args.basedir
    basedir = input.filename("basedir: ", basedir, verify=util.verify_dir_exists_writable)
    setup["basedir"] = basedir

    if mi is not None:
        mi.result = True
        #        mi.label = "CHANGED!"
        mi.description = "description goes here"
        io.echo(f"setbasedir.120: {mi.status=}", level="debug")

    return True


#    return mi
