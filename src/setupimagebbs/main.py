import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import lib

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
  return None

def main(args, **kw):
    bbsengine.util.heading("setup image bbs!")
    lib.setarea(args, "setupimagebbs", **kw)
    ttyio.inputstring("press almost any key:")

    # ttyio.echo("args=%r" % (args), level="debug")

    locale.setlocale(locale.LC_ALL, "")

    terminalwidth = ttyio.getterminalwidth()

    ttyio.echo("{f6:3}{cursorup:3}")
    initscreen(bottommargin=1)

    def preprompthook(args):
      bbsengine.setarea("setup image bbs main menu")

    if args.basedir is True and args.debug is True:
      ttyio.echo("setupbbs.main.120: basedir=%r" % (args.basedir))
#    args.basedir = os.path.expanduser(args.basedir)
#    args.basedir = os.path.expandvars(args.basedir)
#    args.basedir = ttyio.inputstring("basedir: ", args.basedir, args=args)

    localhost = checklocalhostdns(args)

#    checktcpser(args)
    checkvice(args)
#    tcpser(args)
#    gfd3(args)
#    defaultconfig(args)

    menuitems = [
      { "name": "setbasedir",     "callback": "setbasedir",     "label": "set base dir", "result":(True, "test")},
      { "name": "loadjson",       "callback": "loadjson",       "label": "load setup settings from json file"},
      { "name": "modem",          "callback": "modem",          "label": "modem"},
      { "name": "displaysync",    "callback": "displaysync",    "label": "display"},
      { "name": "sound",          "callback": "sound",          "label": "sound"},
      { "name": "iosettings",     "callback": "iosettings",     "label": "i/o settings"},
      { "name": "drive",          "callback": "drive",          "label": "drives"},
      { "name": "defaultconfig",  "callback": "defaultconfig",  "label": "use default config before setting options"},
      { "name": "saveonviceexit", "callback": "saveonviceexit", "label": "save settings on exit from vice"},
      { "name": "confirmonexit",  "callback": "confirmonexit",  "label": "confirm before exit from vice"},
      { "name": "savejson",       "callback": "savejson",       "label": "save setup settings to json file"},
    ]

#    bbsengine.setarea("main menu")
    menu = bbsengine.menu.Menu("image bbs setup", menuitems, args=args)
    menu.run("setup main menu: ", preprompthook)
#    summary()
#    savejson()

    return
