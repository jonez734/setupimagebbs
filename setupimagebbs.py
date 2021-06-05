import os
import re
import json
import locale
import socket
import argparse
import readline
import subprocess
import ttyio4 as ttyio

vicecommandline = {}
tcpsercommandline = {}
localhost = "localhost"
ioaddrs = {}
setup = {}

# @since 20210523
# imported from bbsengine5
def runcallback(args:object, callback:str, **kwargs):
  if callable(callback) is True:
    ttyio.echo("runcallback.420: callable", level="debug")
    return callback(args)

  s = callback.split(".")
  if len(s) > 1:
    modulepath = ".".join(s[:-1])
    functionname = s[len(s)-1:][0]
  else:
    modulepath = None
    functionname = s[0]

  ttyio.echo("runcallback.160: modulepath=%r functionname=%r" % (modulepath, functionname), level="debug", interpret=False)

  if modulepath is not None:
    try:
        m = importlib.import_module(modulepath)
    except ModuleNotFoundError:
        ttyio.echo("runcallback.180: %s module not found" % (modulepath), level="error")
    else:
        ttyio.echo("runcallback.200: m=%r" % (m), level="debug")
        func = getattr(m, functionname)
        ttyio.echo("runcallback.220: func=%r" % (func), level="debug")
        if callable(func) is True:
            func(args, **kwargs)
  else:
    ttyio.echo("runcallback.240: functionname=%r" % (functionname), level="debug")
    try:
      func = eval(functionname)
    except NameError:
      ttyio.echo("runcallback.320: %r not found." % (functionname), level="error")
      return False
    if callable(func) is True:
      ttyio.echo("runcallback.260: callable", level="debug")
      rc = func(args, **kwargs)
    else:
      ttyio.echo("runcallback.280: not callable", level="debug")
      rc = False

  ttyio.echo("runcallback.300: callback completed", level="debug")
  return rc

def initscreen(topmargin=0, bottommargin=0):
  terminalheight = ttyio.getterminalheight()
  # ttyio.echo("initscreen.100: terminalheight=%r" % (terminalheight))
  ttyio.echo("{decsc}{decstbm:%d,%d}{decrc}" % (topmargin, terminalheight-bottommargin))

# updatebottombar() - imported from ttyio4
# @since 20210222
def updatebottombar(buf:str) -> None:
  size = ttyio.getterminalsize()
  terminalheight = ttyio.getterminalheight()
  terminalwidth = ttyio.getterminalwidth()
  buf = buf.ljust(terminalwidth-2, " ")
  ttyio.echo("{decsc}{/all}{curpos:%d,0}%s{el}{decrc}" % (terminalheight, buf), wordwrap=False, end="")
  return

def displaymenu(menuitems:list, title:str=None, default=None):
  terminalwidth = ttyio.getterminalwidth()
  # ttyio.echo("terminalwidth=%r" % (terminalwidth), level="debug")

  maxlen = 0
  for m in menuitems:
        l = len(m["label"])
        if l > maxlen:
            maxlen = l

  firstline = False
  ttyio.echo(" {white}{bggray}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)
  if title is None or title == "":
    ttyio.echo(" {white}{bggray} {black}{acs:ulcorner}{acs:hline:%d}{black}{acs:urcorner}{bggray}  {/all}" % (terminalwidth - 7))
  else:
    ttyio.echo(" {white}{bggray} {lightblue}{acs:ulcorner}{acs:hline:%d}{acs:urcorner}{bggray}  {/all}" % (terminalwidth - 7))
    ttyio.echo(" {white}{bggray} {lightblue}{acs:vline}{black}%s{black[C}{acs:vline}{bgblack} {bggray} {/all}" % (title.center(terminalwidth-7)))
    ttyio.echo(" {white}{bggray} {lightblue}{acs:ltee}{acs:hline:%d}{acs:rtee}{bgblack} {bggray} {/all}" % (terminalwidth - 7))
  ch = ord("A")
  options = ""
  for m in menuitems:
      buf = "[%s] %s" % (chr(ch), m["label"])
      if firstline is True:
          ttyio.echo(" {white}{bggray} {black}{black} %s {bggray}  {/all}" % (buf.ljust(terminalwidth-7)), wordwrap=False)
          firstline = False
      else:
          ttyio.echo(" {white}{bgblack} {black}{acs:vline}{cyan}%s {lightblue}{acs:vline}{bgblack} {bggray} {/all}" % (buf.ljust(terminalwidth-8)), wordwrap=False)
      options += chr(ch)
      ch += 1

  ttyio.echo(" {white}{bggray} {black}{acs:vline}%s {black}{acs:vline}{bgblack} {bggray} {/all}" % (" "*(terminalwidth-8)), wordwrap=False)

  ttyio.echo(" {bggray} {black}{acs:vline}{black}%s {black}{acs:vline}{bgblack} {bggray} {/all}" % ("[Q] quit".ljust(terminalwidth-8)), wordwrap=False)
  options += "Q"

  ttyio.echo(" {white}{bggray} {black}{acs:llcorner}{acs:hline:%d}{acs:lrcorner}{bgblack} {bggray} {/all}" % (terminalwidth-7))

  ttyio.echo(" {white}{bggray}  {bgblack}%s {bggray} {/all}" % (" "*(terminalwidth-6)), wordwrap=False)
  ttyio.echo(" {bggray}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)
  return

def resolverequires(args, menuitems, name):
  def find(name):
    for m in menuitems:
      if name == m["name"]:
        return m
    else:
      return None

#  ttyio.echo("resolverequires.140: name=%r" % (name), interpret=False)
  menuitem = find(name)
#  ttyio.echo("resolverequires.160: menuitem=%r" % (menuitem), interpret=False)
  if menuitem is None:
#    ttyio.echo("resolverequires.160: name=%r not found" % (name))
    return None

  res = None
  requires = menuitem["requires"] if "requires" in menuitem else ()
#  ttyio.echo("resolverequires.200: requires=%r" % (requires,), interpret=False)
  if len(requires) == 0:
    return True

  res = None
  for r in requires:
    m = find(r)
#    ttyio.echo("resolverequires.180: r=%r m=%r" % (r, m), interpret=False)
    if m is None:
      return False
    if "result" in m:
      if m["result"] is False:
        return False
    else:
      return False
  return True

def handlemenu(args:object, menuitems:list, prompt:str, title:str=None, default=None):
  terminalwidth = ttyio.getterminalwidth()
  maxlen = 0
  for m in menuitems:
    l = len(m["label"])+4
    if l > maxlen:
      maxlen = l

  ttyio.echo("handlemenu.100: maxlen=%r title=%r" % (maxlen, title), level="debug")
  ttyio.echo(" {white}{bgblue}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)
  if title is None or title == "":
    ttyio.echo(" {white}{bgblue} {lightblue}{acs:ulcorner}{acs:hline:%d}{acs:urcorner}{bgblue}  {/all}" % (terminalwidth - 7))
  else:
    ttyio.echo(" {white}{bgblue} {lightblue}{acs:ulcorner}{acs:hline:%d}{acs:urcorner}{bgblue}  {/all}" % (terminalwidth - 7))
    ttyio.echo(" {white}{bgblue} {lightblue}{acs:vline}{bgcyan}{black}%s{bgblue}{lightblue}{acs:vline}{bgblack} {bgblue} {/all}" % (title.center(terminalwidth-7)))
    ttyio.echo(" {white}{bgblue} {lightblue}{acs:ltee}{acs:hline:%d}{acs:rtee}{bgblack} {bgblue} {/all}" % (terminalwidth - 7))
  ch = ord("A")
  options = ""
  for m in menuitems:
    if "result" in m:
      result = m["result"]
      if type(result) == tuple:
        resultbuf = ""
        r, s = result
        if r is True:
          resultbuf = s
        result = "%s" % (resultbuf)
      else:
        result = "(%r)" % (result)
    else:
      result = ""
    requires = m["requires"] if "requires" in m else ()

    if len(requires) == 0:
      requiresbuf = ""
    else:
      requiresbuf = "(requires: %s)" % (ttyio.readablelist(requires))
    name = m["name"] if "name" in m else None
    if resolverequires(args, menuitems, name) is True:
      buf = "[%s] %s %s %s" % (chr(ch), m["label"], result, requiresbuf)
      ttyio.echo(" {black}{bgblue} {lightblue}{acs:vline}{bgcyan}{black} %s {bgblue}{lightblue}{acs:vline}{bgblack} {bgblue} {/all}" % (buf.ljust(terminalwidth-9)), wordwrap=False)
    else:
      buf = "[%s] %s %s %s" % (chr(ch), m["label"], result, requiresbuf)
      ttyio.echo(" {black}{bgblue} {lightblue}{acs:vline}{bgcyan}{black} {bggray}{white}%s {bgblue}{lightblue}{acs:vline}{bgblack} {bgblue} {/all}" % (buf.ljust(terminalwidth-9)), wordwrap=False)
    bufstripped = ttyio.interpretmci(buf, strip=True)
    # ttyio.echo(" {black}{bgblue} {lightblue}{acs:vline}{bgcyan}{black} %s {bgblue}{lightblue}{acs:vline}{bgblack} {bgblue} {/all}" % (buf.ljust(terminalwidth-len(bufstripped))), wordwrap=False)
    options += chr(ch)
    ch += 1
  ttyio.echo(" {black}{bgblue} {lightblue}{acs:vline}{bgcyan} %s {bgblue}{lightblue}{acs:vline}{bgblack} {bgblue} {/all}" % (" "*(terminalwidth-9)), wordwrap=False)
  ttyio.echo(" {black}{bgblue} {lightblue}{acs:vline}{black}{bgcyan} %s {bgblue}{lightblue}{acs:vline}{bgblack} {bgblue} {/all}" % ("[Q] Quit".ljust(terminalwidth-9)), wordwrap=False)
  options += "Q"

  ttyio.echo(" {bgblue} {lightblue}{acs:llcorner}{acs:hline:%s}{acs:lrcorner}{bgblack} {bgblue} {/all}" % (terminalwidth-7), wordwrap=False)
  ttyio.echo(" {white}{bgblue}  {bgblack}%s{bgblue} {/all}" % (" "*(terminalwidth-5)), wordwrap=False)
  ttyio.echo(" {white}{bgblue}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)
  ch = ttyio.inputchar(prompt, options, "Q")
  if ch == "Q":
    ttyio.echo("quit")
    return None

  i = ord(ch) - ord("A")
  mi = menuitems[i]
  callback = mi["callback"]
  label = mi["label"]
  name = mi["name"]
  ttyio.echo("%s" % (label))
#  ttyio.echo("handlemenu.100: %r" % (mi), level="debug", interpret=False)
  if resolverequires(args, menuitems, name) is False:
    if ttyio.inputboolean("requirements not resolved. proceed? [y{bggray}N{/all}]: ", "N", "YN") is False:
      ttyio.echo("aborted.")
      return False
  res = runcallback(args, callback)
  mi["result"] = res
  return res

def title(title:str, titlecolor:str="{bgray}{white}", hrcolor:str="{white}", hrchars:str="{acs:hline}", llcorner="{acs:llcorner}", lrcorner="{acs:lrcorner}", ulcorner="{acs:ulcorner}", urcorner="{acs:urcorner}", width=None):
  if width is None:
    width = ttyio.getterminalwidth()-2

  ttyio.echo("{/all}%s%s{acs:hline:%s}%s" % (hrcolor, ulcorner, width, urcorner), end="")
  ttyio.echo("{f6}{white}{acs:vline}{bggray}{white}%s{/all}{white}{acs:vline}{/all}" % (title.center(width)), end="")
  ttyio.echo("{f6}{white}%s{acs:hline:%s}%s{/all}" % (llcorner, width, lrcorner))
  return

def area(buf):
  width = ttyio.getterminalwidth()

  updatebottombar("{bggray}{white} %s {/all}" % (buf.ljust(width-2, " ")))
  return

def sound(args):
  status = []
  if ttyio.inputboolean("enable sound? [Yn]: ", "Y", "YN") is False:
    vicecommandline["+sound"] = None
    if "-sound" in vicecommandline:
      del vicecommandline["-sound"]
    return True
  if "+sound" in vicecommandline:
    del vicecommandline["+sound"]
  # -soundrate
  # -soundbufsize
  # -soundfragsize
  # -soundsync
  d = vicecommandline["-soundsync"] if "-soundsync" in vicecommandline else "0"
  ch = ttyio.inputchar("soundsync 0: system 1: mono 2: stereo: ", "012", d)
  vicecommandline["-soundsync"] = ch
  if ch == "0":
    ttyio.echo("system")
    status.append("sync: system")
  elif ch == "1":
    ttyio.echo("mono")
    status.append("sync: mono")
  elif ch == "2":
    ttyio.echo("stereo")
    status.append("sync: stereo")
  # -soundsuspend
  # -soundvolume
  d = vicecommandline["-soundvolume"] if "-soundvolume" in vicecommandline else "70"
  vol = ttyio.inputinteger("soundvolume (0-100): ", d)
  vicecommandline["-soundvolume"] = vol
  status.append("vol: %s" % (vol))
  # -sounddev
  d = vicecommandline["-sounddev"] if "-sounddev" in vicecommandline else "P"
  opts = []
  if d == "P":
    opts.append("{bggray}{white}[P]ulse{/all}")
  else:
    opts.append("[P]ulse")
  if d == "A":
    opts.append("{bggray}{white}{A]LSA{/all}")
  else:
    opts.append("[A]LSA")
  if d == "S":
    opts.append("{bggray}{white}[S]DL{/all}")
  else:
    opts.append("[S]DL")
  if d == "D":
    opts.append("{bggray}{white}[D]ummy{/all}")
  else:
    opts.append("[D]ummy")
  dev = ttyio.inputchar("%s: " % (" ".join(opts)), "PASD", d)
  if dev == "P":
    ttyio.echo("Pulse")
    vicecommandline["-sounddev"] = "pulse"
    status.append("dev: pulse")
  elif dev == "A":
    ttyio.echo("ALSA")
    vicecommandline["-sounddev"] = "alsa"
    status.append("dev: alsa")
  elif dev == "S":
    ttyio.echo("SDL")
    vicecommandline["-sounddev"] = "sdl"
    status.append("dev: sdl")
  elif dev == "D":
    ttyio.echo("Dummy")
    vicecommandline["-sounddev"] = "dummy"
    status.append("dev: dummy")

  return (True, (ttyio.readablelist(status)))

def truedrive(args):
  area("vice: truedrive")
  title("vice: truedrive")
  if "-truedrive" in vicecommandline:
    defaultvalue = "Y"
  elif "+truedrive" in vicecommandline:
    defaultvalue = "N"
  else:
    defaultvalue = "Y"

  if defaultvalue == "Y":
    ch = ttyio.inputboolean("truedrive? [{bggray}{white}Y{/all}n]: ", "Y", "YN")
  else:
    ch = ttyio.inputboolean("truedrive? [y{bggray}{white}N{/all}]: ", "N", "YN")

  if ch is True:
    if "+truedrive" in vicecommandline:
      del vicecommandline["+truedrive"]
    vicecommandline["-truedrive"] = None
  else:
    if "-truedrive" in vicecommandline:
      del vicecommandline["-truedrive"]
    vicecommandline["+truedrive"] = None

def drivesound(args):
  area("vice: drivesound")
  title("vice: drivesound")

  if ttyio.inputboolean("Enable sound emulation of disk drives? [{bggray}{white}Y{/all}n]: ", "Y", "YN") is True:
    volume = ttyio.inputinteger("drive sound volume? [0-4000]: ", 100)
    if "+drivesound" in vicecommandline:
      del vicecommandline["+drivesound"]
    vicecommandline["-drivesound"] = None
    vicecommandline["-drivesoundvolume"] = volume
  else:
    if "-drivesound" in vicecommandline:
      del vicecommandline["-drivesound"]
    if "-drivesoundvolume" in vicecommandline:
      del vicecommandline["-drivesoundvolume"]
    vicecommandline["+drivesound"] = None
  resultbuf = "(disabled)"
  if "-drivesound" in vicecommandline:
    resultbuf = "(enabled, volume=%s)" % (vicecommandline["-drivesoundvolume"])
  return (True, resultbuf)

def clock(args):
  area("vice: clock")
  title("clock")
  # clock1 = ds12c887rtc(args)
  clock1 =  ttyio.inputboolean("use ds12c887rtc? [{bggray}{white}Y{/all}n]: ", "Y", "YN")
  if clock1 is False:
    clock2 = ttyio.inputboolean("use cmd fd-4000 RTC? [y{bggray}{white}N{/all}]: ", "N", "YN")
  else:
    clock2 = ttyio.inputboolean("use cmd fd-4000 RTC? [{bggray}{white}Y{/all}n]: ", "Y", "YN")

  if clock1 is True and clock2 is True:
    if ttyio.inputboolean("do you really want to use both the cmd rtc and ds12c887rtc? [yN]: ", "N", "YN") is False:
      ttyio.echo("aborted", level="error")
      return False

  if clock2 is True:
    cmd4000(args)
  status = []
  if clock1 is True:
    status.append("ds12c887rtc")
  if clock2 is True:
    status.append("cmd fd-4000rtc")
  statusbuf = "(%s)" % (ttyio.readablelist(status))

  return (True, statusbuf)

def checklocalhostdns(args):
  area("system: check for 'localhost' in dns")
  try:
    res = socket.gethostbyname("localhost")
  except:
    ttyio.echo("dns check for 'localhost' failed, reverting to ipv4 address 127.0.0.1", level="warn")
    return "127.0.0.1"
  else:
    ttyio.echo("dns check for 'localhost' passed", level="success")
    return "localhost"

def verifyFileExistsReadable(args, filename):
  filename = os.path.expanduser(filename)
  filename = os.path.expandvars(filename)
  if args.debug is True:
    ttyio.echo("args=%r filename=%r" % (args, filename))

  if os.access(filename, os.R_OK) is True and os.path.isfile(filename) is True:
    return True
  return False

def inputfilename(args, prompt, default, verify=verifyFileExistsReadable, **kw):
  ttyio.echo("inputfilename.120: args=%r" % (args))
  if default is not None:
    default = os.path.expanduser(default)
    default = os.path.expandvars(default)
  if args.basedir is not None and default is not None:
    default = os.path.join(args.basedir, default)
  if args.debug is True:
    ttyio.echo("inputfilename.100: delims=%r" % (readline.get_completer_delims()))
  return ttyio.inputstring(prompt, default, verify=verify, completerdelims="\t\n", args=args, **kw)

def gfd3(args):
  if ttyio.inputboolean("use storage settings for 'gfd3'? [Yn]: ", "Y", "YN") is True:
    vicecommandline["-10"] = os.path.join(args.basedir, "drive10.d81")
    vicecommandline["-11"] = os.path.join(args.basedir, "drive11.d81")
    vicecommandline["-drive10type"] = "1581"
    vicecommandline["-drive11type"] = "1581"
    vicecommandline["-ltkimage0"] = os.path.join(args.basedir, "drive8-0.dlk")
    vicecommandline["-ltkimage1"] = os.path.join(args.basedir, "drive8-1.dlk")
    vicecommandline["-ltkimage2"] = os.path.join(args.basedir, "drive8-2.dlk")
  return True

def keyboard(args):
  area("vice: keyboard")
  title("keyboard")

  keyboards = ("0: Symbpolic", "1: Positional", "2: symbolic (user)", "3: positional (user)")
  ch = ttyio.inputchar("Specify index of keymap file ({bggray}{white}0:symbolic{/all}, 1:positional, 2:symbolic (user), 3:positional (user))? [0123]: ","0123", "0")
  if ch == "0":
    resultbuf = "symbolic"
  elif ch == "1":
    resultbuf = "positional"
  elif ch == "2":
    resultbuf = "symbolic (user)"
  elif ch == "3":
    resultbuf = "positional (user)"
  else:
    resultbuf = ""

  vicecommandline["-keymap"] = ch
  return (True, resultbuf)

def cmd4000(args):
  area("vice: cmd4000")
  title("device 9 cmd 4000")
  if ttyio.inputboolean("enable cmd fd-4000 on device 9? [Yn]: ", "Y", "YN") is True:
    vicecommandline["-dos4000"] = inputfilename(args, "dos4000 filename: ", "cmd-fd-4000-dos-v1.40-fd-350022.bin")
    vicecommandline["-drive9type"] = "4000"
    if ttyio.inputboolean("enable drive 9 rtc save? [Yn]: ", "Y", "YN") is True:
      vicecommandline["-drive9rtcsave"] = None
    else:
      vicecommandline["+drive9rtcsave"] = None

def inputioaddr(args, optionslist:list, currentvalue:str, defaultvalue:str):
  pass

def ds12c887rtc(args):
  area("vice: ds12c887rtc")
  title("ds12c887rtc")
  if "-ds12c887rtc" in vicecommandline:
    ch = ttyio.inputboolean("Enable DS12C887RTC? [{bggray}{white}Y{/all}n]: ", "Y", "YN")
  elif "+ds12c887rtc" in vicecommandline:
    ch = ttyio.inputboolean("Enable DS12C887RTC? [y{bggray}{white}N{/all}]: ", "N", "YN")
  else:
    ch = ttyio.inputboolean("Enable DS12C887RTC? [{bggray}{white}Y{/all}n]: ", "Y", "YN")

  if ch is False:
    vicecommandline["+ds12c887rtc"] = None
    if "-ds12c887rtc" in vicecommandline:
      del vicecommandline["-ds12c887rtc"]
    return True
  else:
    vicecommandline["-ds12c887rtc"] = None
    if "+ds12c887rtc" in vicecommandline:
      del vicecommandline["+ds12c887rtc"]

  if "-ds12c887rtcsave" in vicecommandline:
    ch = ttyio.inputboolean("Enable saving of the DS12C887RTC data when changed? [{bggray}{white}Y{/all}n]: ", "Y", "YN")
  elif "+ds12c887rtcsave" in vicecommandline:
    ch = ttyio.inputboolean("Enable saving of the DS12C887RTC data when changed? [y{bggray}{white}N{/all}]: ", "N", "YN")
  else:
    ch = ttyio.inputboolean("Enable saving of the DS12C887RTC data when changed? [{bggray}{white}Y{/all}n]: ", "Y", "YN")

  if ch is False:
    vicecommandline["+ds12c887rtcsave"] = None
  else:
    vicecommandline["-ds12c887rtcsave"] = None

  addresschoices = ["0xD500","0xD600","0xD700", "0xDE00","0xDF00"]

  currentaddr = vicecommandline["-ds12c887rtcbase"] if "-ds12c887rtcbase" in vicecommandline else None

  defaultvalue = "0xD700"

  menu = []
  ch = ord("A")
  options = ""
  for c in addresschoices:
    i = ch - ord("A")
    if currentaddr == addresschoices[i] or defaultvalue == addresschoices[i]:
      menu.append("{bggray}{white}[%s] %s{/all}" % (chr(ch), addresschoices[i]))
      defaultvalue = chr(ch)
    elif currentaddr in ioaddrs:
      menu.append("{darkgray}[%s] %s{/all}" % (chr(ch), addresschoices[i]))
    else:
      menu.append("[%s] %s" % (chr(ch), addresschoices[i]))
    options += chr(ch)
    ch += 1

  ch = ttyio.inputchar("ioaddr "+" ".join(menu)+": ", options, defaultvalue, noneok=False)
  addr = addresschoices[ord(ch) - ord("A")]
  ttyio.echo(addr)
  if addr in ioaddrs:
    if ttyio.inputboolean("that address is already used for %s. proceed? [y{bggray}{white}N{/all}]: " % (ioaddrs[addr]), "N", "YN") is True:
      vicecommandline["-ds12c887rtcbase"] = addr
      ioaddrs[addr] = "ds12c887rtc"

  # -ds12c887rtchalted -> Set the RTC oscillator to 'halted'
  # -ds12c887rtcrunning -> Set the RTC oscillator to 'running'
  if "-ds12c887rtcrunning" in vicecommandline:
    ch = ttyio.inputchar("Set the RTC oscillator to {bggray}{white}[R]unning{/all} or [H]alted: ", "RH", "R")
  elif "-ds12c887rtchalted" in vicecommandline:
    ch = ttyio.inputchar("Set the RTC oscillator to [R]unning or {bggray}{white}[H]alted{/all}: ", "RH", "H")
  else:
    ch = ttyio.inputchar("Set the RTC oscillator to {bggray}{white}[R]unning{/all} or [H]alted: ", "RH", "R")

  if ch == "R":
    ttyio.echo("Running")
    vicecommandline["-ds12c887rtcrunning"] = None
    if "-ds12c887rtchalted" in vicecommandline:
      del vicecommandline["-ds12c887rtchalted"]
  elif ch == "H":
    ttyio.echo("Halted")
    vicecommandline["-ds12c887rtchalted"] = None
    if "-ds12c887rtcrunning" in vicecommandline:
      del vicecommandline["-ds12c887rtcrunning"] 

  if ch is False:
    vicecommandline["-ds12c887running"] = None
    if "-ds12c887halted" in vicecommandline:
      del vicecommandline["-ds12c887halted"]
  else:
    vicecommandline["-ds12c887halted"] = None
    if "-ds12c887running" in vicecommandline:
      del vicecommandline["-ds12c887running"]

  ttyio.echo()
  return True

def rs232(args):
  area("vice: rs232/ip232")
  title("vice: rs232/ip232")
  dev = int(ttyio.inputchar("device [1-4]: ", "1234", "4"))
  vicecommandline["+rsuser"] = None
  vicecommandline["-rsdev%d" % (dev)] = "%s:%s" % (localhost, tcpsercommandline["-v"])
  vicecommandline["-rsdev%dip232" % (dev)] = None
  vicecommandline["-rsdev%dbaud" % (dev)] = tcpsercommandline["-s"] # 38400

  ttyio.echo("configured rsdev%d as ip232." % (dev))
  return True

def acia(args):
  area("vice")
  title("vice: acia")

  if ttyio.inputboolean("Enable the ACIA RS232 interface emulation (Swiftlink)? [Yn]: ", "Y", "YN") is False:
    vicecommandline["+acia1"] = None
    return True

  d = vicecommandline["-acia1mode"] if "-acia1mode" in vicecommandline else "B"

  options = {
    "A": "normal",
    "B": "swiftlink",
    "C": "turbo32"
  }

  prompt = []
  o = ""
  for k, v in options.items():
    if d == k:
      prompt.append("{bggray}{white}[%s] %s{/all}" % (k, v))
    else:
      prompt.append("[%s] %s" % (k, v))
    o += k

  promptbuf = "set the ACIA mode %s: [ABC]? " % (" ".join(prompt))

  ch = ttyio.inputchar(promptbuf, "ABC", d)
  if ch in options:
    ttyio.echo("%s: %s" % (ch, options[ch]))
#  if ch == "A":
#    ttyio.echo("A: Normal")
#  elif ch == "B":
#    ttyio.echo("B: Swiftlink")
#  elif ch == "C":
#    ttyio.echo("C: Turbo32")

  status = []

  vicecommandline["-acia1mode"] = ord(ch) - ord("A")

  # $de00 is not supported by ml30
  ch = ttyio.inputchar("Base address of the ACIA cartridge ({bggray}{white}A: 0xDE00{/all}, B: 0xDF00): ", "AB", "A")
  if ch == "A":
    ttyio.echo("A: 0xDE00")
    vicecommandline["-acia1base"] = "0xDE00"
    ioaddrs["0xDE00"] = "acia1"
    status.append("io: 0xDE00")
  else:
    ttyio.echo("B: 0xDF00")
    vicecommandline["-acia1base"] = "0xDF00"
    ioaddrs["0xDF00"] = "acia1"
    status.append("io: 0xDF00")

  if "-aciairq" in vicecommandline:
    default = vicecommandline["-aciairq"]
  else:
    default = "B"

  if default == "A":
    ttyio.echo("{bggray}{white}[A] None{/all}")
  else:
    ttyio.echo("[A] None")
  if default == "B":
    ttyio.echo("{bggray}{white}[B] NMI{/all}")
  else:
    ttyio.echo("[B] NMI")
  if default == "C":
    ttyio.echo("{bggray}{white}[C] IRQ{/all}")
  else:
    ttyio.echo("[C] IRQ")
  ch = ttyio.inputchar("Set the ACIA interrupt (A: None, {bggray}{white}[B]: NMI{/all}, C: IRQ): ", "012", default)
  if ch == "A":
    vicecommandline["-acia1irq"] = 0
    ttyio.echo("A: None")
    status.append("interrupts: None")
  elif ch == "B":
    vicecommandline["-acia1irq"] = 1
    ttyio.echo("B: NMI")
    status.append("interrupts: NMI")
  elif ch == "C":
    ttyio.echo("C: IRQ")
    vicecommandline["-acia1irq"] = 2
    status.append("interrupts: IRQ")

  default = "D"

  ttyio.echo("[A] serial1")
  ttyio.echo("[B] serial2")
  ttyio.echo("[C] serial3")
  ttyio.echo("[D] serial4")
  ch = ttyio.inputchar("acia device [ABCD]: ", "ABCD", default)
  n = ord(ch) - ord("A")
  vicecommandline["-myaciadev"] = n
  ttyio.echo("serial%d" % (n+1))
  status.append("serial%d" % (n+1))
  # vicecommandline["-myaciadev"] = 3 # serial4
  vicecommandline["-acia1"] = None
  return (True, "("+" ".join(status)+")")

def checktcpser(args, filename="tcpser"): # filename="/home/jam/tmp/tcpser-1.1.4/tcpser"):
  area("tcpser")
  title("tcpser: check")

  res = subprocess.run([filename, "-V"], capture_output=True, text=True)

  TCPSERVERSTRING = "(TCPSER) 1.1.4_vicekludge"

  # look for "invalid option -- 'V'" -- (-V added in 1.1.4, older versions will complain of invalid option)
  # ttyio.echo("%r" % (res.stderr))
  # ttyio.echo("stdout=%r" % (res.stdout))
  if res.stdout.find("invalid option -- 'V'") > -1 or res.stderr.find("invalid option -- 'V'") > -1:
    ttyio.echo("The version of tcpser installed is not compatible with imagebbs (>=1.1.4).")
    return False

  if res.stdout.find(TCPSERVERSTRING) > -1 or res.stderr.find(TCPSERVERSIONSTRING) > -1:
    ttyio.echo("The version of tcpser installed should be compatible with imagebbs")
    return True

def checkvice(args, filename="x64sc"):
  area("vice")
  title("vice: check")

  res = subprocess.run([filename, "--features"], capture_output=True, text=True)

  for match in re.finditer(r"^(\S+)\s+(yes|no)\s+(.*)", res.stdout, re.MULTILINE):
    define = match.group(1)
    value = True if match.group(2) ==  "yes" else False
    description = match.group(3)
    if define == "HAVE_RS232NET":
      ttyio.echo("{bold}%s: %s (%s){/all}" % (description, value, define))
      if value is False:
        ttyio.echo("{bgred}{white}HAVE_RS232NET is not enabled.{/all}")
        return False
      else:
        ttyio.echo("{bggreen}{lightgreen}HAVE_RS232NET is enabled{/all}")
        return True
    return None

class completeVocab(object):
  def __init__(self, args, vocab):
      # ttyio.echo("completeAttributeName.100: called")
      self.vocab = vocab

  # @log_exceptions
  def complete(self:object, text:str, state:int):
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

def phonebook(args):
  book = []
  book.append({"alias": "ci1", "host": "cib.dyndns.org:6400", "sysop": "x-tec", "system": "Image 1.2"})
  book.append({"alias": "ci2", "host": "cib.dyndns.org:6401", "sysop": "x-tec", "system": "Image 1.2"})

## X-Tec
#-n ci1=cib.dyndns.org:6400		\ # Image 1.2
#-n ci2=cib.dyndns.org:6401		\ # Image 1.2
#-n ci3=cib.dyndns.org:6402		\ # Image 1.2
#-n tst=cib.dyndns.org:6403		\ # Image 1.2b, SD2IEC test BBS
## 1st Wrong Number 1
#-n wn1=cib.dyndns.org:6404		\ # Image 1.2b
# 2nd Wrong Number 2
#-n wn2=cib.dyndns.org:6405		\ # Image 2.0
# Image 2.0 HQ
#-n hq2=cib.dyndns.org:6407		\ # Image 2.0, test board
# CAPTAIN SULU - System One
#-n sys=systemone.ddns.net:6400		\ # Image 1.2b
# Blackflag - Alternate Dimension
#-n altd=altd.dyndns.org:6400		\ # Image 1.2
# Darkstar - Atlantis & Avalon Isle
#-n atl=atl.ddns.org:6401		\ # Image 2.0
#-n avi=avalonisle.ddns.net		\ # Image 1.2b
# Jay Theriot - Bayou BBS
#-n bay=jayctheriot.com:6401		\ # Image 1.2b
# Deadman - Remote CPU
#-n cpu=remotecpu.com:6502		\ # Image 1.2b
## S0RC3R0R - Retrograde
#-n rtg=retrograde.dyndns.org:6400	\ # Image 2.0
## J.ROTTEN - Riktronics
#-n rik=rkbbs.net:23			\ # Image 1.2a
## Hoy Brothers - 13th Floor
#-n 13f=13th.hoyvision.com:6400		\ # Image 1.3


def tcpser(args):
  area("tcpser")
  title("tcpser")

  # ttyio.echo("tcpser.120: vicecommandline=%r" % (vicecommandline), interpret=False)
  if ttyio.inputboolean("invert DCD pin? [Yn]: ", "Y", "YN") is True:
    tcpsercommandline["-I"] = None

  acia1mode = vicecommandline["-acia1mode"] if "-acia1mode" in vicecommandline else None
  ttyio.echo("tcpser.120: acia1mode=%r" % (acia1mode), level="debug")
  if args.debug is True:
    ttyio.echo("tcpser.100: acia1mode=%r" % (acia1mode), level="debug")
  if acia1mode == 1:
    speed = 38400
  else:
    speed = 2400

  tcpsercommandline["-s"] = ttyio.inputinteger("speed in bits per second (-s): ", speed)

  tcpsercommandline["-v"] = ttyio.inputinteger("tcp port for VICE RS232NET (-v): ", 25232)
  tcpsercommandline["-p"] = ttyio.inputstring("port or address:port (-p): ", "6400")

  tcpsercommandline["-i"] = ttyio.inputstring("modem init string (-i): at", "e0v0s0=1s2=27")

  title("tcpser: trace flags")

  traceflags = ""
  if ttyio.inputboolean("modem input (s) [Yn]: ", "Y", "YN") is True:
    traceflags += "s"
  if ttyio.inputboolean("modem output (S) [yN]: ", "N", "YN") is True:
    traceflags += "S"
  if ttyio.inputboolean("IP input (i) [yN]: ", "N", "YN") is True:
    traceflags += "i"
  if ttyio.inputboolean("IP output (I) [Yn]: ", "Y", "YN") is True:
    traceflags += "I"
  if len(traceflags) > 0:
    tcpsercommandline["-t"] = traceflags

  vocab = ["none", "fatal", "error", "warn", "info", "debug", "enter-exit", "all"]
  buf = ttyio.inputstring("Logging Level (-l): ", "all", completer=completeVocab(args, vocab), verify=verifyLoggingLevelName)
  level = None
  for i in range(0, len(vocab)):
    if vocab[i] == buf:
      level = i
      break

  if args.debug is True:
    ttyio.echo("level=%r" % (i))
  tcpsercommandline["-l"] = i
  return True

def ramlink(args):
  area("vice")
  title("vice: ramlink")

  if args.ramlink is True:
    ttyio.echo("use ramlink? Yes (command line option)")
  else:
    if ttyio.inputboolean("use ramlink? ", "N", "YN") is False:
          vicecommandline["-ramlink"] = None
          return True

  vicecommandline["+ramlink"] = None

  if ttyio.inputboolean("rtc save? ", "Y", "YN") is True:
      vicecommandline["-rtcsave"] = None
  else:
      vicecommandline["+rtcsave"] = None

  if ttyio.inputboolean("allow write to ramlink image? ", "Y", "YN") is True:
      vicecommandline["-ramlinkimagerw"] = None
  else:
      vicecommandline["+ramlinkimagerw"] = None

  vicecommandline["-ramlinksize"] = ttyio.inputinteger("RAMLINK RAMCARD size in MiB (0=Disabled): ", "1")

  vicecommandline["-cartramlink"] = inputfilename(args, "ramlink bin: ", "ramlink.bin")

  return True

def displaysync(args):
  area("vice")
  title("vice: display sync")
  sync = ttyio.inputchar("{bggray}{white}[N]TSC{/all} or [P]AL? ", "NP", "N")
  if sync == "N":
    ttyio.echo("NTSC")
    vicecommandline["-ntsc"] = None
    resultbuf = "(NTSC)"
  elif sync == "P":
    ttyio.echo("PAL")
    vicecommandline["-pal"] = None
    resultbuf = "(PAL)"
  return (True, resultbuf)

def drivetype(args, devicenumber, oldvalue=None):
    types = {
        "1540":    "CBM 1540",
        "1541":    "CBM 1541",
        "1541-II": "CBM 1541-II",
        "1570":    "CBM 1570",
        "1571":    "CBM 1571",
        "1581":    "CBM 1581"
    }

    if "-dos4000" in vicecommandline and vicecommandline["-dos4000"] is not None:
      # types["2000"] = "CMD FD-2000"
      types["4000"] = "CMD FD-4000"
  
    if args.debug is True:
      ttyio.echo("drivetype.100: oldvalue=%r" % (oldvalue))

    default = "N"
    options = "N"
    menu = {}
    char = ord("A")
    for k, v in types.items():
      if k == oldvalue:
        ttyio.echo("{bggray}{white}[%s] %s{/all}" % (chr(char), v))
        default = chr(char)
      else:
        ttyio.echo("[%s] %s" % (chr(char), v))

      options += chr(char)

      menu[chr(char)] = k

      char += 1

    if default == "N":
      ttyio.echo("{bggray}{white}[N] None{/all}")
    else:
      ttyio.echo("[N] None")

    dt = ttyio.inputchar("device %d type: " % (devicenumber), options, default)
    # ttyio.echo("menu=%r" % (menu), interpret=False)
    if dt in menu:
        ttyio.echo("%s" % (menu[dt]))
        return menu[dt]
    ttyio.echo("None")
    return "0"

def verifyLTKDevInRange(args, val):
  val = int(val)
  if val < 8 or val > 99:
    ttyio.echo("ltk device number (%d) out of range." % (val))
    return False
  return True

def storage(args):
#  area("vice: storage")
#  title("vice: storage")

  useltk = setup["useltk"] if "useltk" in setup else True
  usecmd = setup["usecmd"] if "usecmd" in setup else False

  if useltk is True:
    ltk = ttyio.inputboolean("use ltk? [{bggray}{white}Y{/all}n]: ", "Y", "YN")
  else:
    ltk = ttyio.inputboolean("use ltk? [y{bggray{white}N]: ", "N", "YN")
  if usecmd is True:
    cmd = ttyio.inputboolean("use cmd? [{bggray}{white}Y{/all}n]: ", "Y", "YN")
  else:
    cmd = ttyio.inputboolean("use cmd? [y{bggray{white}N]: ", "N", "YN")

  setup["useltk"] = ltk
  setup["usecmd"] = cmd

  # handle hybrid!
  if ltk is True:
      ttyio.echo("Lt. Kernel")

#      setup["useltk"] = True
      ltkdevdefault = setup["ltkdev"] if "ltkdev" in setup else 8
      ltkdev = ttyio.inputinteger("ltk device number, 8..99: ", ltkdevdefault, verify=verifyLTKDevInRange)
      if ltkdev < 12 and ltkdev > 7:
        vicecommandline["-drive%dtype" % (ltkdev)] = "1581"

      setup["ltkdev"] = ltkdev
      vicecommandline["-cartcrt"] = inputfilename(args, "-cartcrt: ", "ltk.crt")
      vicecommandline["-ltkimage0"] = inputfilename(args, "-ltkimage0: ", "drive8-0.dlk")
      vicecommandline["-ltkimage1"] = inputfilename(args, "-ltkimage1: ", "drive8-1.dlk")
      vicecommandline["-ltkimage2"] = inputfilename(args, "-ltkimage2: ", "drive8-2.dlk")
      vicecommandline["-ltkport"] = ttyio.inputstring("Set LTK port number (0..15): ", "0", verify=verifyLTKPortInRange)

      # handle existing value
      ch = vicecommandline["-ltkio"] = ttyio.inputchar("Set LTK IO page (0: $DE00, {bggray}{white}1: $DF00{/all}): ", "01", "1")
      if ch == "1":
        ttyio.echo("1: $DF00")
        ioaddrs["0xDF00"] = "ltkio"
        if "0xDE00" in ioaddrs and ioaddrs["0xDE00"] == "ltkio":
          del ioaddrs["0xDE00"]
      elif ch == "0":
        ttyio.echo("0: 0xDE00")
        ioaddrs["0xDE00"] = "ltkio"
        if "0xDF00" in ioaddrs and ioaddrs["0xDF00"] == "ltkio":
          del ioaddrs["0xDF00"]
      vicecommandline["-ltkio"] = ch

      ch = ttyio.inputboolean("use ltk dos72-s1 disk on device 9? [yN]: ", "N", "YN")
      if ch == "Y":
        vicecommandline["-9"] = "dos72-s1.d64"
        vicecommandline["-drive9type"] = "1541"
      elif ch == "N":
        ttyio.echo("No")
  if cmd is True:
#    setup["usecmd"] = True
    ttyio.echo("CMD")
    if "-ltkio" in vicecommandline and vicecommandline["-ltkio"] is not None and setup["ltkdev"] == 8:
      ttyio.echo("ltk assigned to drive %s" % (ltkdev))
      if ttyio.inputboolean("proceed? [yN]: ", "N", "YN") is True:
        vicecommandline["-8"] =  "dos-part1.dhd" # what device type?
        vicecommandline["-drive8type"] = "4844"

    vicecommandline["-9"] =  "cmddrive9.d4m"
    vicecommandline["-drive9type"] = "4000"

    vicecommandline["-10"] = "cmddrive10.d4m"
    vicecommandline["-drive10type"] = "4000"

    vicecommandline["-11"] = "cmddrive11.d4m"
    vicecommandline["-drive11type"] = "4000"

  for drivenumber in range(8,11+1):
    default = None
    option = "-drive%dtype" % (drivenumber)
    #ttyio.echo("main.100: option=%r" % (option))
    #ttyio.echo("main.120: vicecommandline=%r" % (vicecommandline), interpret=False)
    if option in vicecommandline:
      default = vicecommandline[option]
    dt = drivetype(args, drivenumber, default)
    if dt is not None:
      vicecommandline[option] = dt

    dn = "drive%drtcsave" % (drivenumber)
    if dt == "4000" or dt == "2000" or dt == "4844":
      if ttyio.inputboolean("Enable saving of RTC data to drive %d? [Yn]: " % (drivenumber), "Y", "YN") is True:
        vicecommandline["-%s" % (dn)] = None
        if "+%s" % (dn) in vicecommandline:
          del vicecommandline["+%s" % (dn)]
      else:
        vicecommandline["+%s" % (dn)] = None
        if "-%s" % (dn) in vicecommandline:
          del vicecommandline["-%s" % (dn)]

    default = None

    option = "-%d" % (drivenumber)

    if option in vicecommandline:
      default = vicecommandline[option]

    if dt != "0":
      if args.debug is True:
        ttyio.echo("storage.160: default=%r" % (default), level="debug")
      image = inputfilename(args, "drive %d image: " % (drivenumber), default, noneok=True, multiple=False)
      if image is not None:
        vicecommandline[option] = image

  result = []
  for r in range(8, 11+1):
    ttyio.echo("storage.120: r=%r" % (r))
    dt = "-drive%dtype" % (r)
    if dt in vicecommandline:
      v = vicecommandline[dt]
      if setup["useltk"] is True and "ltkdev" in setup and r == setup["ltkdev"]:
        result.append("%d: LTK (fallback: %s)" % (r, v))
      else:
        result.append("%d: %s" % (r, v))
  # ttyio.echo("storage.100: result=%r" % (result), interpret=False)
  return (True, " ".join(result))

def summary(args):
  area("setupimagebbs")
  title("summary")
  if "-default" in vicecommandline:
    resetdefaults = True
    del vicecommandline["-default"]
  else:
    resetdefaults = False

  for k, v in ioaddrs.items():
    ttyio.echo("k=%r, v=%r" % (k, v))

  opts = []

  if resetdefaults is True:
    opts.append("-default")

  for k, v in vicecommandline.items():
    if v is not None:
      buf = "%s %s" % (k, v)
    else:
      buf = "%s" % (k)

    opts.append(buf)

  ttyio.echo("x64sc %s" % (" \\{f6} ".join(opts)), wordwrap=False)

  opts = []
  for k, v in tcpsercommandline.items():
    if v is not None:
      buf = "%s %s" % (k, v)
    else:
      buf = "%s" % (k)

    opts.append(buf)
    # ttyio.echo(buf)

  ttyio.echo("tcpser %s" % (" ".join(opts)))

  return

def defaultconfig(args):
  area("vice")

  if ttyio.inputboolean("restore default config before processing options? [Yn]: ", "Y", "YN") is True:
    vicecommandline["-default"] = None
  return True

def saveonviceexit(args):
  area("vice")
  title("vice: save settings on vice exit")

  if ttyio.inputboolean("save vice settings on exit from vice? [Yn]: ", "Y", "YN") is True:
    vicecommandline["-saveres"] = None
  else:
    vicecommandline["+saveres"] = None
  return True

def checkltkaciaconflict(args):
  area("setupimagebbs")
  title("vice: check for ltk / acia1 conflicts")

  ttyio.echo("check ltk and acia1 conflicts: ",end="")
  if "-aciabase" not in vicecommandline or "-ltkio" not in vicecommandlist:
    ttyio.echo("ltk or acia not defined.")
    return True

  if vicecommandline["-acia1base"] == vicecommandline["-ltkio"]:
      ttyio.echo("conflict.{f6}acia1base and ltkio are set to the same value (%s)" % (vicecommandline["-acia1base"]))
      return False
  return True

def savejson(args):
  area("setupimagebbs")
  title("save json file of setup data")
  
  if ttyio.inputboolean("save setup data? [Yn]: ", "Y", "YN") is False:
    ttyio.echo("setup data {bold}not{/bold} saved.{f6}")
    return True

  data = {}

  data["setup"] = {}
  data["vice"] = {}
  for k, v in vicecommandline.items():
    data["vice"][k] = v

  data["tcpser"] = {}
  for k, v in tcpsercommandline.items():
    data["tcpser"][k] = v

  data["setup"] = {}
  for k, v in setup.items():
    data["setup"][k] = v

  if args.debug is True:
    ttyio.echo("data=%r" % (data), interpret=False)

  default = os.path.join(args.basedir, "gfd3.json")
  default = os.path.expandvars(default)
  default = os.path.expanduser(default)

  filename = inputfilename(args, "save json: ", default, noneok=True, multiple=False, verify=None)
  if filename is None:
    ttyio.echo("aborted.")
    return True
  fp = open(filename, "w")
  fp.write(json.dumps(data))
  fp.close()
  return True

def edata(args):
  data = []
  data.append({"record": 21, "type": "inputchar", "prompt": "System Reservation Password", "choices": ["0=None", "1=Once", "2=All"], "options": "012", "default": "0"})
  data.append({"record": 32, "type": "inputchar", "prompt": "RS232 Device", "choices": ["0=User Port", "1=Swiftlink"], "options": "01", "default": "1"})
  data.append({"record": 38, "type": "inputltkdevice", "prompt": "LTK device number", "default": "8"})
  data.append({"record": 43, "type": "inputstring", "prompt": "Password Mask Char", "default": "X"})
  data.append({"record": 47, "type": "inputstring", "prompt": "BBS Name", "default": "not Galaxy Federation 3"})
  data.append({"record": 51, "type": "inputbbsid", "prompt": "BBS Identifier", "default": "GF"})
  data.append({"record": 52, "type": "inputdevicedrive", "prompt": "System Device, Drive", "default": "8,1"})
  data.append({"record": 53, "type": "inputdevicedrive", "prompt": "E-Mail Device, Drive", "default": "8,2"})
  data.append({"record": 54, "type": "inputdevicedrive", "prompt": "Etcetera Device, Drive", "default": "8,1"})
  data.append({"record": 55, "type": "inputdevicedrive", "prompt": "Directory", "default": "8,0"})
  data.append({"record": 56, "type": "inputdevicedrive", "prompt": "Modules", "default": "8,0"})
  data.append({"record": 57, "type": "inputdevicedrive", "prompt": "User", "default": "8,1"})
  data.append({"record": 58, "type": "inputnewusercredits", "prompt": "Credits for new user", "default": "100"})

def iocollisionhandler(args):
  title("iocollision handling")
  if "-iocollision" in vicecommandline:
    default = ord("A") + int(vicecommandline["-iocollision"])
  else:
    default = "B"

  if default == "A":
    ttyio.echo("{bggray}{white}[A] error message, detatch all involved carts{/all}")
  else:
    ttyio.echo("[A] error message, detatch all involved carts")

  if default == "B":
    ttyio.echo("{bggray}{white}[B] error message, detach most recent involved cart{/all}")
  else:
    ttyio.echo("[B] error message, detach most recent involved cart")
  
  if default == "C":
    ttyio.echo("{bggray}{white}[C] warning in log, bitwise-and valid return values{/all}")
  else:
    ttyio.echo("[C] warning in log, bitwise-and valid return values")

  ch = ttyio.inputchar("iocollision handling [ABC]: ", "ABC", default)
  if ch == "A":
    ttyio.echo("A: detach all involved carts")
  elif ch == "B":
    ttyio.echo("B: detach most recent involved cart")
  elif ch == "C":
    ttyio.echo("C: warn, bitwise-and valid return values")
  val = ord(ch) - ord("A")
  # ttyio.echo("val=%r" % (val), level="debug")
  vicecommandline["-iocollision"] = val
  return True

def main():
    # parser = OptionParser(usage="usage: %prog [options] projectid")
    parser = argparse.ArgumentParser("setupimagebbs")
    
    # parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    
    # parser.add_option("--debug", default=False, action="store_true", help="run %prog in debug mode")
    parser.add_argument("--debug", action="store_true", default=False, dest="debug")

    parser.add_argument("--storage", action="store", choices=["ltk", "cmd"], dest="storage")
    parser.add_argument("--ramlink", action="store_true", dest="ramlink")
    parser.add_argument("--basedir", action="store", dest="basedir", default="~jam/projects/gfd3/")
    args = parser.parse_args()
    # ttyio.echo("args=%r" % (args), level="debug")

    locale.setlocale(locale.LC_ALL, "")

    terminalwidth = ttyio.getterminalwidth()

    ttyio.echo("{f6:5}{curpos:%d,0}" % (ttyio.getterminalheight()-3))
    initscreen(bottommargin=1)

    area("setup image bbs v3.0")

    if args.debug is True:
        ttyio.echo("setupbbs.main.100: args=%r" % (args))

    if args.basedir and args.debug is True:
      ttyio.echo("setupbbs.main.120: basedir=%r" % (args.basedir))
    args.basedir = os.path.expanduser(args.basedir)
    args.basedir = os.path.expandvars(args.basedir)
    args.basedir = ttyio.inputstring("basedir: ", args.basedir, args=args)

    localhost = checklocalhostdns(args)

    checktcpser(args)
    checkvice(args)
#    tcpser(args)
    gfd3(args)
    defaultconfig(args)

    menuitems = [
#      { "callback": "checktcpser", "label": "check tcpser" },
#      { "callback": "checkvice", "label": "check vice"},
#      { "callback": "gfd3",          "label": "use gfd3 config"},
      { "name": "acia",          "callback": "acia",          "label": "acia setup", "requires":()},
      { "name": "tcpser",        "callback": "tcpser",        "label": "tcpser parameters", "requires":("acia",)},
      { "name": "rs232",         "callback": "rs232",         "label": "rs232/ip232", "requires": ("tcpser", "acia",)},
      { "name": "drivesound",    "callback": "drivesound",    "label": "drive sound"},
      { "name": "displaysync",   "callback": "displaysync",   "label": "displaysync"},
      { "name": "clock",         "callback": "clock",         "label": "rtc (real-time clock)"},
      { "name": "storage",       "callback": "storage",       "label": "storage"},
      { "name": "keyboard",      "callback": "keyboard",      "label": "keyboard settings"},
      { "name": "ramlink",       "callback": "ramlink",       "label": "ramlink"},
      { "name": "sound",         "callback": "sound",         "label": "sound"}
    ]
    done = False
    while not done:
      res = handlemenu(args, menuitems, "setup: ")
      ttyio.echo("main.100: res=%r" % (res,))
      if res is True:
        ttyio.echo("OK", level="success")
        continue
      elif res is False:
        ttyio.echo("FAILED", level="error")
        if ttyio.inputboolean("proceed anyway? [yN]: ", "N", "YN") is False:
          done = True
      elif res is None:
        done = True
      elif type(res) == type(()):
        ttyio.echo("tuple")
      else:
        ttyio.echo("??? res=%r" % (res,))
#      "iocollisionhandler",
#      "checkltkaciaconflict",
#      "saveonviceexit",
#    )

#    for t in tests:
#      if args.debug is True:
#        ttyio.echo("t=%r" % (t), level="debug")
#      func = eval(t)
#      if callable(func) is False:
#        ttyio.echo("%r is not callable." % (t), level="error")
#        continue
#      res = func(args)
#      if res is False:
#        if ttyio.inputboolean("{bgred}{black} %r failed. {/all}{f6}proceed anyway? [Yn]: " % (t), "Y", "YN") is False:
#          ttyio.echo("{bgred}{black} aborted {/all}", end="", level="error")
#          return False
#      ttyio.echo()

#    summary()
#    savejson()

    return    

if __name__ == "__main__":
  try:
    main()
  finally:
    terminalheight = ttyio.getterminalheight()
    ttyio.echo("{curpos:%d,0}{el}{reset}{/all}" % (terminalheight))
