import locale

import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import lib
from . import module

def init(args, **kw):
    ttyio.setvariable("engine.menu.boxcharcolor", "{bglightgray}{darkgreen}")
    ttyio.setvariable("engine.menu.color", "{bggray}")
    ttyio.setvariable("engine.menu.shadowcolor", "{bgdarkgray}")
    ttyio.setvariable("engine.menu.cursorcolor", "{bglightgray}{blue}")
    ttyio.setvariable("engine.menu.boxcolor", "{bgblue}{green}")
    ttyio.setvariable("engine.menu.itemcolor", "{blue}{bglightgray}")
    ttyio.setvariable("engine.menu.titlecolor", "{black}{bglightgray}")
    ttyio.setvariable("engine.menu.promptcolor", "")
    ttyio.setvariable("engine.menu.inputcolor", "{white}")
    ttyio.setvariable("engine.menu.disableditemcolor", "{darkgray}")
    ttyio.setvariable("engine.menu.resultfailedcolor", "{bgred}{white}")

    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
  return None

def main(args, **kw):

    bbsengine.util.heading("setup image bbs!")
    lib.setarea(args, "setupimagebbs", **kw)

    # ttyio.echo("args=%r" % (args), level="debug")

    locale.setlocale(locale.LC_ALL, "")

    terminalwidth = ttyio.getterminalwidth()

    bbsengine.screen.init()

    setup = {}
    vice = {}
    tcpser = {}

    def preprompthook(args):
      bbsengine.setarea("setup image bbs main menu")

    if args.basedir is True and args.debug is True:
      ttyio.echo(f"setupbbs.main.120: {basedir=}", level="debug")
#    args.basedir = os.path.expanduser(args.basedir)
#    args.basedir = os.path.expandvars(args.basedir)
#    args.basedir = ttyio.inputstring("basedir: ", args.basedir, args=args)

    module.runsubmodule(args, "checklocalhostdns", setup=setup, vice=vice, **kw)

    module.runsubmodule(args, "checktcpser", tcpser=tcpser, **kw) # checktcpser(args)

    if module.runsubmodule(args, "checkvice") is False:
     ttyio.echo("vice check failed!", level="error") # checkvice(args)
     
#    setup["test"] = 42
    ttyio.echo(f"1 {setup=}", level="debug")
    module.runsubmodule(args, "setbasedir", setup=setup, **kw)
    ttyio.echo(f"2 {setup=}", level="debug")
#    return

#    tcpser(args)
#    gfd3(args)
#    defaultconfig(args)

    menuitems = [
#     bbsengine.menu.Item("A", "set base dir for json files", "setbasedir"),
     bbsengine.menu.Item("A", "load settings from json file", "loadjson", requires=None),
     bbsengine.menu.Item("B", "modem settings", "modem"), # { "name": "modem",          "module": "modem",          "label": "modem"},
     bbsengine.menu.Item("C", "display", "displaysync"),
     bbsengine.menu.Item("D", "sound", "sound"),
     bbsengine.menu.Item("J", "confirm on vice exit", "confirmonexit"),
#     bbsengine.menu.Item("E", "iosettings", "iosettings"),
#     bbsengine.menu.Item("G", "drive", "drives"),
     # "D": { "name": "displaysync",    "module": "displaysync",    "label": "display"},
     # "E": { "name": "sound",          "module": "sound",          "label": "sound"},
     # "F": { "name": "iosettings",     "module": "iosettings",     "label": "i/o settings"},
     # "G": { "name": "drive",          "module": "drive",          "label": "drives"},
     # "H": { "name": "defaultconfig",  "module": "defaultconfig",  "label": "use default config before setting options"},
     # "I": { "name": "saveonviceexit", "module": "saveonviceexit", "label": "save settings on exit from vice"},
     # "J": { "name": "confirmonexit",  "module": "confirmonexit",  "label": "confirm before exit from vice"},
     # "K": { "name": "savejson",       "module": "savejson",       "label": "save setup settings to json file"},
    ]

    bbsengine.screen.setarea("image bbs setup")

    menu = bbsengine.menu.Menu(args, "image bbs setup", menuitems)

    done = False
    while not done:
     res = menu.run("main menu: ", preprompthook)
     if res.menuitem.key == "X":
      ttyio.echo("exit")
      break

     res = module.runsubmodule(args, res.menuitem.module, tcpser=tcpser, menuitem=res.menuitem, setup=setup, vice=vice, **kw)

    # bbsengine.menu.Item("J", "confirm on vice exit", "confirmonexit"),
    res = module.runsubmodule(args, "confirmonexit", setup=setup, vice=vice, tcpser=tcpser, **kw)
    res = module.runsubmodule(args, "summary", setup=setup, vice=vice, tcpser=tcpser, **kw) # summary()
    res = module.runsubmodule(args, "savejson", setup=setup, vice=vice, tcpser=tcpser, **kw) # savejson()


    return
