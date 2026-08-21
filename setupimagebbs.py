#
# Copyright (C) 2023 zoidtechnologies.com. All Rights Reserved.
#

import os
import locale
import argparse
import subprocess

import ttyio5 as ttyio
import bbsengine5 as bbsengine

vicecommandline = {}
tcpsercommandline = {}
edata = {}
localhost = "localhost"
ioaddrs = {}
setup = {}
rtcdevices = []


def initscreen(topmargin=0, bottommargin=0):
    terminalheight = ttyio.getterminalheight()
    # ttyio.echo("initscreen.100: terminalheight=%r" % (terminalheight))
    ttyio.echo(
        "{decsc}{decstbm:%d,%d}{decrc}" % (topmargin, terminalheight - bottommargin)
    )


# updatebottombar() - imported from ttyio4
# @since 20210222
def updatebottombar(buf: str) -> None:
    size = ttyio.getterminalsize()
    terminalheight = ttyio.getterminalheight()
    terminalwidth = ttyio.getterminalwidth()
    buf = buf.ljust(terminalwidth - 2, " ")
    ttyio.echo(
        "{decsc}{/all}{curpos:%d,0}%s{el}{decrc}" % (terminalheight, buf),
        wordwrap=False,
        end="",
    )
    return


# def title(title:str, titlecolor:str="{bgray}{white}", hrcolor:str="{white}", hrchars:str="{acs:hline}", llcorner="{acs:llcorner}", lrcorner="{acs:lrcorner}", ulcorner="{acs:ulcorner}", urcorner="{acs:urcorner}", width=None):
#  if width is None:
#    width = ttyio.getterminalwidth()-2
#
#  ttyio.echo("{/all}%s%s{acs:hline:%s}%s" % (hrcolor, ulcorner, width, urcorner), end="")
#  ttyio.echo("{f6}{white}{acs:vline}{bggray}{white}%s{/all}{white}{acs:vline}{/all}" % (title.center(width)), end="")
#  ttyio.echo("{f6}{white}%s{acs:hline:%s}%s{/all}" % (llcorner, width, lrcorner))
#  return


def area(buf):
    width = ttyio.getterminalwidth()
    updatebottombar(
        "{var:setupimagebbs.areacolor} %s {/all}" % (buf.ljust(width - 2, " "))
    )
    return


# def verifyFileExistsReadable(args, filename):
#  filename = os.path.expanduser(filename)
#  filename = os.path.expandvars(filename)
#  if args is not None and args.debug is True:
#    ttyio.echo("args=%r filename=%r" % (args, filename))
#
#  if os.access(filename, os.R_OK) is True and os.path.isfile(filename) is True:
#    return True
#  return False

# def inputfilename(args, prompt, default, verify=verifyFileExistsReadable, **kwargs):
#  ttyio.echo("inputfilename.120: args=%r" % (args))
#  if default is not None:
#    default = os.path.expanduser(default)
#    default = os.path.expandvars(default)
#  if args is not None and args.basedir is not None and default is not None:
#    default = os.path.join(args.basedir, default)
#  if args is not None and args.debug is True:
#    ttyio.echo("inputfilename.100: delims=%r" % (readline.get_completer_delims()))
#  return ttyio.inputstring(prompt, default, verify=verify, completerdelims="\t\n", args=args, **kwargs)


def gfd3(args):
    bbsengine.setarea("use gfd3 settings")
    if (
        ttyio.inputboolean(
            "use settings for 'gfd3'? [{var:engine.currentoptioncolor}Y{/all}n]: ",
            "Y",
            "YN",
        )
        is True
    ):
        vicecommandline["-10"] = os.path.join(args.basedir, "drive10.d81")
        vicecommandline["-11"] = os.path.join(args.basedir, "drive11.d81")
        vicecommandline["-drive10type"] = "1581"
        vicecommandline["-drive11type"] = "1581"
        vicecommandline["-ltkimage0"] = os.path.join(args.basedir, "drive8-0.dlk")
        vicecommandline["-ltkimage1"] = os.path.join(args.basedir, "drive8-1.dlk")
        vicecommandline["-ltkimage2"] = os.path.join(args.basedir, "drive8-2.dlk")
    return True


def inputioaddr(args, optionslist: list, currentvalue: str, defaultvalue: str):
    pass


class completeVocab(object):
    def __init__(self, args, vocab):
        # ttyio.echo("completeAttributeName.100: called")
        self.vocab = vocab

    # @log_exceptions
    def complete(self: object, text: str, state: int):
        results = [x for x in self.vocab if x.startswith(text)] + [None]
        return results[state]


def verifyLoggingLevelName(args, buf):
    vocab = ["none", "fatal", "error", "warn", "info", "debug", "enter-exit", "all"]
    if buf in vocab:
        return True
    return False


# @see https://www.digitalocean.com/community/tutorials/how-to-use-subprocess-to-run-external-programs-in-python-3
def verifyC64Cart(args, filename):
    f = os.path.join(args.basedir, filename)
    f = os.path.expanduser(f)
    f = os.path.expandvars(f)
    res = subprocess.run(["file", "--brief", f], capture_output=True, text=True)
    if args.debug is True:
        ttyio.echo("res.stdout=%r" % (res.stdout), level="debug")
    return


def verifyLTKPortInRange(args, port):
    try:
        port = int(port)
    except:
        return False
    if port < 0 or port > 15:
        return False
    return True


def tcpserphonebook(args):
    book = []
    book.append(
        {
            "alias": "ci1",
            "host": "cib.dyndns.org:6400",
            "sysop": "x-tec",
            "system": "Image 1.2",
        }
    )
    book.append(
        {
            "alias": "ci2",
            "host": "cib.dyndns.org:6401",
            "sysop": "x-tec",
            "system": "Image 1.2",
        }
    )


## X-Tec
# -n ci1=cib.dyndns.org:6400		\ # Image 1.2
# -n ci2=cib.dyndns.org:6401		\ # Image 1.2
# -n ci3=cib.dyndns.org:6402		\ # Image 1.2
# -n tst=cib.dyndns.org:6403		\ # Image 1.2b, SD2IEC test BBS
## 1st Wrong Number 1
# -n wn1=cib.dyndns.org:6404		\ # Image 1.2b
# 2nd Wrong Number 2
# -n wn2=cib.dyndns.org:6405		\ # Image 2.0
# Image 2.0 HQ
# -n hq2=cib.dyndns.org:6407		\ # Image 2.0, test board
# CAPTAIN SULU - System One
# -n sys=systemone.ddns.net:6400		\ # Image 1.2b
# Blackflag - Alternate Dimension
# -n altd=altd.dyndns.org:6400		\ # Image 1.2
# Darkstar - Atlantis & Avalon Isle
# -n atl=atl.ddns.org:6401		\ # Image 2.0
# -n avi=avalonisle.ddns.net		\ # Image 1.2b
# Jay Theriot - Bayou BBS
# -n bay=jayctheriot.com:6401		\ # Image 1.2b
# Deadman - Remote CPU
# -n cpu=remotecpu.com:6502		\ # Image 1.2b
## S0RC3R0R - Retrograde
# -n rtg=retrograde.dyndns.org:6400	\ # Image 2.0
## J.ROTTEN - Riktronics
# -n rik=rkbbs.net:23			\ # Image 1.2a
## Hoy Brothers - 13th Floor
# -n 13f=13th.hoyvision.com:6400		\ # Image 1.3


def verifyLTKDevInRange(args, val):
    val = int(val)
    if val < 8 or val > 99:
        ttyio.echo("ltk device number (%d) out of range." % (val), level="error")
        return False
    return True


storagedevices = StorageDevices()


def defaultconfig(args, **kwargs):
    bbsengine.setarea("vice: default config")

    status = []
    if (
        ttyio.inputboolean(
            "restore default config before processing options? [{var:engine.currentoptioncolor}Y{/all}n]: ",
            "Y",
            "YN",
        )
        is True
    ):
        vicecommandline["-default"] = None
        status.append("Yes")
    elif "-default" in vicecommandline:
        del vicecommandline["-default"]
        status.append("No")

    bbsengine.poparea()
    return (True, status)


def basedir(args):
    pass


def findioaddr(value):
    #  ttyio.echo("findioaddr.100: ioaddrs=%r" % (ioaddrs), interpret=False)
    # return key not value
    for k, v in ioaddrs.items():
        if value == v:
            return k
    return


def preprompthook(args):
    result = []
    f = findioaddr("ltkio")
    if f is not None and f != "0xDF00":
        result.append("LTKIO conflict")
    #  ttyio.echo("f=%r" % (f), level="debug")
    f = findioaddr("acia1base")
    if f is not None and f != "0xDE00":
        result.append("ACIA1BASE conflict")
    #  ttyio.echo("acia1base f=%r" % (f), level="debug")
    #  ttyio.echo("result=%r" % (result), level="debug")
    #  area = bbsengine.oxfordcomma(result)
    #  bbsengine.setarea(area)
    return


def setbasedir(args, **kwargs):
    global setup

    basedir = setup["basedir"] if "basedir" in setup else args.basedir
    basedir = bbsengine.inputfilename(args, "basedir: ", basedir)
    setup["basedir"] = basedir
    return (True, basedir)


def check(args):
    ip232found = False
    for dev in (1, 2, 3, 4):
        if "-rsdev%dip232" % (dev) in vicecommandline:
            ip232found = True
            break

    if "-ltkio" in vicecommandline:
        pass


def main():
    parser = argparse.ArgumentParser("setupimagebbs")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", default=False, dest="debug")
    parser.add_argument(
        "--basedir", action="store", dest="basedir", default="~jam/projects/gfd3/"
    )
    args = parser.parse_args()
    # ttyio.echo("args=%r" % (args), level="debug")

    locale.setlocale(locale.LC_ALL, "")

    terminalwidth = ttyio.getterminalwidth()

    ttyio.echo("{f6:3}{cursorup:3}")
    initscreen(bottommargin=1)

    def preprompthook(args):
        bbsengine.setarea("setup image bbs main menu")

    #    ttyio.echo("setting variables")
    ttyio.setvariable("engine.menu.boxcharcolor", "{bglightgray}{darkgreen}")
    ttyio.setvariable("engine.menu.color", "{bggray}")
    ttyio.setvariable("engine.menu.shadowcolor", "{bgdarkgray}")
    ttyio.setvariable("engine.menu.cursorcolor", "{bglightgray}{blue}")
    ttyio.setvariable("engine.menu.boxcolor", "{bgblue}{green}")
    ttyio.setvariable("engine.menu.itemcolor", "{blue}{bglightgray}")
    ttyio.setvariable("engine.menu.titlecolor", "{black}{bglightgray}")
    ttyio.setvariable("engine.menu.promptcolor", "{lightgray}")
    ttyio.setvariable("engine.menu.inputcolor", "{white}")
    ttyio.setvariable("engine.menu.disableditemcolor", "{darkgray}")
    ttyio.setvariable("engine.menu.resultfailedcolor", "{bgred}{white}")
    ttyio.setvariable("engine.currentoptioncolor", "{bggray}{white}")
    #    ttyio.setvariable("engine.areacolor", "{bggray}{white}")

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
        {
            "name": "setbasedir",
            "callback": setbasedir,
            "label": "set base dir",
            "result": (True, "test"),
        },
        {
            "name": "loadjson",
            "callback": loadjson,
            "label": "load setup settings from json file",
        },
        {"name": "modem", "callback": modem, "label": "modem"},
        {"name": "displaysync", "callback": displaysync, "label": "display"},
        {"name": "sound", "callback": sound, "label": "sound"},
        {"name": "iosettings", "callback": iosettings, "label": "i/o settings"},
        {"name": "drive", "callback": drive, "label": "drives"},
        {
            "name": "defaultconfig",
            "callback": defaultconfig,
            "label": "use default config before setting options",
        },
        {
            "name": "saveonviceexit",
            "callback": saveonviceexit,
            "label": "save settings on exit from vice",
        },
        {
            "name": "confirmonexit",
            "callback": confirmonexit,
            "label": "confirm before exit from vice",
        },
        {
            "name": "savejson",
            "callback": savejson,
            "label": "save setup settings to json file",
        },
    ]

    #    bbsengine.setarea("main menu")
    menu = bbsengine.Menu("image bbs setup", menuitems, args=args)
    menu.run("setup main menu: ", preprompthook)
    #    summary()
    #    savejson()

    return


if __name__ == "__main__":
    try:
        main()
    except EOFError:
        ttyio.echo("{decrc}{/all}{bold}EOF{/bold}")
    except KeyboardInterrupt:
        ttyio.echo("{decrc}{/all}{bold}INTR{/bold}")
    finally:
        terminalheight = ttyio.getterminalheight()
        ttyio.echo("{curpos:%d,0}{el}{reset}{/all}" % (terminalheight))
