import argparse

import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import lib
from . import _version

def init(args=None, **kw):
#    ttyio.setvariable("empyre.highlightcolor", "{bggray}{white}")
#    ttyio.echo("empyre.boot.init", level="debug")
    return True

def access(args, op, **kw):
    if args.debug is True:
        ttyio.echo(f"setupimagebbs.module.access.100: {args=} {op=} {kw=}", level="debug")
    return True

def buildargs(args=None, **kw):
    parser = argparse.ArgumentParser("setupimagebbs")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")

#    defaults = {"databasename": "zoid6", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
#    bbsengine.database.buildargdatabasegroup(parser, defaults)

    return parser
    
def main(args, **kw):
    if args is not None and "debug" in args and args.debug is True:
        ttyio.echo(f"setupimagebbs.module.main.100: args={args!r}", level="debug")

    bbsengine.util.heading("setup image bbs")

#    if args.debug is True:
#        ttyio.echo("database: %s host: %s:%s" % (args.databasename, args.databasehost, args.databaseport), level="debug")

    lib.setarea(args, None, "startup %s rev %s" % (_version.__datestamp__, _version.__version__))

    if runsubmodule(args, "main", **kw) is False:
        ttyio.echo("error running submodule 'main'", level="error")
    return    

def checkmodule(args, module, **kw):
    module = f"{lib.PACKAGENAME}.{module}"
    return bbsengine.module.check(args, module, **kw)

def runmodule(args, module, **kw):
    module = f"{lib.PACKAGENAME}.{module}"
    if args.debug is True:
        ttyio.echo(f"setupimagebbs.module.runmodule.100: {module=}", level="debug")

    if bbsengine.module.check(args, module, **kw) is False:
        ttyio.echo(f"setupimagebbs.module.runmodule.120: module {module} not available", level="error")
        return False

    return bbsengine.module.runmodule(args, module, **kw)

def runsubmodule(args, submodule, **kw):
    if args.debug is True:
        ttyio.echo(f"setupimagebbs.module.runsubmodule.100: {submodule=}", level="debug")
    return runmodule(args, submodule, **kw)
