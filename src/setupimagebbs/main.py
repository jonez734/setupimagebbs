import locale

from bbsengine6 import io, util, screen, menu

from . import lib


def init(args, **kw):
    io.setvariable("engine.menu.boxcharcolor", "{bglightgray}{darkgreen}")
    io.setvariable("engine.menu.color", "{bggray}")
    io.setvariable("engine.menu.shadowcolor", "{bgdarkgray}")
    io.setvariable("engine.menu.cursorcolor", "{bglightgray}{blue}")
    io.setvariable("engine.menu.boxcolor", "{bgblue}{green}")
    io.setvariable("engine.menu.itemcolor", "{blue}{bglightgray}")
    io.setvariable("engine.menu.titlecolor", "{black}{bglightgray}")
    io.setvariable("engine.menu.promptcolor", "")
    io.setvariable("engine.menu.inputcolor", "{white}")
    io.setvariable("engine.menu.disableditemcolor", "{darkgray}")
    io.setvariable("engine.menu.resultfailedcolor", "{bgred}{white}")

    return True


def access(args, op, **kw):
    return True


def buildargs(args, **kw):
    return None


def main(args, **kw):
    util.heading("setup image bbs!")
    lib.setarea(args, "setupimagebbs", **kw)

    # ttyio.echo("args=%r" % (args), level="debug")

    locale.setlocale(locale.LC_ALL, "")

    terminalwidth = io.getterminalwidth()

    screen.init()

    setup = {}
    vice = {}
    tcpser = {}

    def preprompthook(args):
        setarea("setup image bbs main menu")

    if args.basedir is True and args.debug is True:
        io.echo(f"setupbbs.main.120: {basedir=}", level="debug")
    #    args.basedir = os.path.expanduser(args.basedir)
    #    args.basedir = os.path.expandvars(args.basedir)
    #    args.basedir = ttyio.inputstring("basedir: ", args.basedir, args=args)

    lib.runmodule(args, "checklocalhostdns", setup=setup, vice=vice, **kw)

    lib.runmodule(args, "checktcpser", tcpser=tcpser, **kw)  # checktcpser(args)

    if lib.runmodule(args, "checkvice") is False:
        io.echo("vice check failed!", level="error")  # checkvice(args)

    #    setup["test"] = 42
    io.echo(f"1 {setup=}", level="debug")
    lib.runmodule(args, "setbasedir", setup=setup, **kw)
    io.echo(f"2 {setup=}", level="debug")
    #    return

    #    tcpser(args)
    #    gfd3(args)
    #    defaultconfig(args)

    menuitems = [
        #     bbsengine.menu.Item("A", "set base dir for json files", "setbasedir"),
        menu.Item("A", "load settings from json file", "loadjson", requires=None),
        menu.Item(
            "B", "modem settings", "modem"
        ),  # { "name": "modem",          "module": "modem",          "label": "modem"},
        menu.Item("C", "display", "displaysync"),
        menu.Item("D", "sound", "sound"),
        menu.Item("J", "confirm on vice exit", "confirmonexit"),
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

    screen.setarea("image bbs setup")

    mainmenu = menu.Menu(args, "image bbs setup", menuitems)

    done = False
    while not done:
        res = mainmenu.run("main menu: ", preprompthook)
        if res.menuitem.key == "X":
            io.echo("exit")
            break

        res = lib.runmodule(
            args,
            res.menuitem.module,
            tcpser=tcpser,
            menuitem=res.menuitem,
            setup=setup,
            vice=vice,
            **kw,
        )

    # bbsengine.menu.Item("J", "confirm on vice exit", "confirmonexit"),
    res = lib.runmodule(
        args, "confirmonexit", setup=setup, vice=vice, tcpser=tcpser, **kw
    )
    res = lib.runmodule(
        args, "summary", setup=setup, vice=vice, tcpser=tcpser, **kw
    )  # summary()
    res = lib.runmodule(
        args, "savejson", setup=setup, vice=vice, tcpser=tcpser, **kw
    )  # savejson()

    return
