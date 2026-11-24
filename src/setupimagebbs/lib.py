PACKAGENAME = "setupimagebbs"

import argparse
from bbsengine6 import screen, module


def setarea(args, left):
    return screen.setarea(left)


def checkmodule(args, modulename, **kwargs):
    return module.checkmodule(args, f"setupimagebbs.{modulename}", **kwargs)


def runmodule(args, modulename, **kwargs):
    return module.runmodule(args, f"setupimagebbs.{modulename}", **kwargs)


def runcallback(args, callbackname, **kwargs):
    return module.runcallback(args, callbackname, **kwargs)


def buildargs(args: argparse.Namespace, **kwargs) -> argparse.ArgumentParser | None:
    parser = argparse.ArgumentParser("setupimagebbs")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")
    parser.add_argument(
        "--basedir", action="store", dest="basedir", default="$HOME/projects/gfd3/"
    )
    parser.add_argument(
        "--x64scpath", action="store", dest="x64scpath", default="/usr/bin/x64sc"
    )

    #    defaults = {"databasename": "zoid6", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    #    database.buildargdatabasegroup(parser, defaults)

    return parser


def init(args: argparse.Namespace, **kwargs) -> bool | None:
    return True
