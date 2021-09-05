#
# Copyright (C) 2021 zoidtechnologies.com. All Rights Reserved.
#

import os
import re
import json
import locale
import socket
import argparse
from argparse import Namespace
import readline
import subprocess
import ttyio4 as ttyio

# import bbsengine5 as bbsengine # remove this in production!
from bbsengine5 import Menu, runcallback

vicecommandline = {}
tcpsercommandline = {}
localhost = "localhost"
ioaddrs = {}
setup = {}
rtcdevices = []

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

def sound(args, **kwargs):
  status = []
  if ttyio.inputboolean("enable sound? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN") is False:
    vicecommandline["+sound"] = None
    if "-sound" in vicecommandline:
      del vicecommandline["-sound"]
    return (True, ("disabled"))
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
    opts.append("{var:setupimagebbs.currentoption}[P]ulse{/all}")
  else:
    opts.append("[P]ulse")
  if d == "A":
    opts.append("{var:setupimagebbs.currentoption}{A]LSA{/all}")
  else:
    opts.append("[A]LSA")
  if d == "S":
    opts.append("{var:setupimagebbs.currentoption}[S]DL{/all}")
  else:
    opts.append("[S]DL")
  if d == "D":
    opts.append("{var:setupimagebbs.currentoption}[D]ummy{/all}")
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

  return (True, (status),)

def truedrive(args, **kwargs):
  area("vice: truedrive")
  title("vice: truedrive")
  if "-truedrive" in vicecommandline:
    defaultvalue = "Y"
  elif "+truedrive" in vicecommandline:
    defaultvalue = "N"
  else:
    defaultvalue = "Y"

  if defaultvalue == "Y":
    ch = ttyio.inputboolean("truedrive? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN")
  else:
    ch = ttyio.inputboolean("truedrive? [y{var:setupimagebbs.currentoptionN{/all}]: ", "N", "YN")

  if ch is True:
    if "+truedrive" in vicecommandline:
      del vicecommandline["+truedrive"]
    vicecommandline["-truedrive"] = None
  else:
    if "-truedrive" in vicecommandline:
      del vicecommandline["-truedrive"]
    vicecommandline["+truedrive"] = None

def drivesound(args, **kwargs):
  area("vice: drivesound")
  title("vice: drivesound")

  if ttyio.inputboolean("Enable sound emulation of disk drives? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN") is True:
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
    return (True, "enabled: vol=%s" % (vicecommandline["-drivesoundvolume"]))
  return (True, resultbuf)

def clock(args, **kwargs):
  area("vice: clock")
  title("clock")
# clock1 = ds12c887rtc(args)
#  clock1 =  ttyio.inputboolean("use ds12c887rtc? [{bggray}{white}Y{/all}n]: ", "Y", "YN")
#  if clock1 is False:
  clock2 = ttyio.inputboolean("use cmd fd-4000 RTC? [y{var:setupimagebbs.currentoption}N{/all}]: ", "N", "YN")
#  else:
#    clock2 = ttyio.inputboolean("use cmd fd-4000 RTC? [{bggray}{white}Y{/all}n]: ", "Y", "YN")

#  if clock1 is True and clock2 is True:
#    if ttyio.inputboolean("do you really want to use both the cmd rtc and ds12c887rtc? [yN]: ", "N", "YN") is False:
#      ttyio.echo("aborted", level="error")
#      return False

  status = []
  if clock2 is True:
    cmd4000(args)
    status.append("cmd fd-4000rtc")
  if len(status) > 0:
    statusbuf = "(%s)" % (ttyio.readablelist(status))
  else:
    statusbuf = ""

  return (True, (status,)) # statusbuf)

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
  if args is not None and args.debug is True:
    ttyio.echo("args=%r filename=%r" % (args, filename))

  if os.access(filename, os.R_OK) is True and os.path.isfile(filename) is True:
    return True
  return False

def inputfilename(args, prompt, default, verify=verifyFileExistsReadable, **kwargs):
  ttyio.echo("inputfilename.120: args=%r" % (args))
  if default is not None:
    default = os.path.expanduser(default)
    default = os.path.expandvars(default)
  if args is not None and args.basedir is not None and default is not None:
    default = os.path.join(args.basedir, default)
  if args is not None and args.debug is True:
    ttyio.echo("inputfilename.100: delims=%r" % (readline.get_completer_delims()))
  return ttyio.inputstring(prompt, default, verify=verify, completerdelims="\t\n", args=args, **kwargs)

def gfd3(args):
  area("use gfd3 settings")
  if ttyio.inputboolean("use settings for 'gfd3'? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN") is True:
    vicecommandline["-10"] = os.path.join(args.basedir, "drive10.d81")
    vicecommandline["-11"] = os.path.join(args.basedir, "drive11.d81")
    vicecommandline["-drive10type"] = "1581"
    vicecommandline["-drive11type"] = "1581"
    vicecommandline["-ltkimage0"] = os.path.join(args.basedir, "drive8-0.dlk")
    vicecommandline["-ltkimage1"] = os.path.join(args.basedir, "drive8-1.dlk")
    vicecommandline["-ltkimage2"] = os.path.join(args.basedir, "drive8-2.dlk")
  return True

def keyboard(args, **kwargs):
  area("vice: keyboard")
  title("keyboard")

  keyboards = ("0: Symbpolic", "1: Positional", "2: symbolic (user)", "3: positional (user)")
  ch = ttyio.inputchar("Specify index of keymap file ({var:setupimagebbs.currentoption}0:symbolic{/all}, 1:positional, 2:symbolic (user), 3:positional (user))? [0123]: ","0123", "0")
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

def cmd4000(args, **kwargs):
  area("vice: cmd4000")
  title("device 9 cmd 4000")
  if ttyio.inputboolean("enable cmd fd-4000 on device 9? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN") is True:
    vicecommandline["-dos4000"] = inputfilename(args, "dos4000 filename: ", "cmd-fd-4000-dos-v1.40-fd-350022.bin")
    vicecommandline["-drive9type"] = "4000"
    if ttyio.inputboolean("enable drive 9 rtc save? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN") is True:
      vicecommandline["-drive9rtcsave"] = None
    else:
      vicecommandline["+drive9rtcsave"] = None

def inputioaddr(args, optionslist:list, currentvalue:str, defaultvalue:str):
  pass

def ds12c887rtc(args, **kwargs):
  area("vice: ds12c887rtc")
  title("ds12c887rtc")
  if "-ds12c887rtc" in vicecommandline:
    ch = ttyio.inputboolean("Enable DS12C887RTC? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN")
  elif "+ds12c887rtc" in vicecommandline:
    ch = ttyio.inputboolean("Enable DS12C887RTC? [y{var:setupimagebbs.currentoption}N{/all}]: ", "N", "YN")
  else:
    ch = ttyio.inputboolean("Enable DS12C887RTC? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN")

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
    ch = ttyio.inputboolean("Enable saving of the DS12C887RTC data when changed? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN")
  elif "+ds12c887rtcsave" in vicecommandline:
    ch = ttyio.inputboolean("Enable saving of the DS12C887RTC data when changed? [y{var:setupimagebbs.currentoption}N{/all}]: ", "N", "YN")
  else:
    ch = ttyio.inputboolean("Enable saving of the DS12C887RTC data when changed? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN")

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
      menu.append("{var:setupimagebbs.currentoption}[%s] %s{/all}" % (chr(ch), addresschoices[i]))
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
    if ttyio.inputboolean("that address is already used for %s. proceed? [y{var:setupimagebbs.currentoption}N{/all}]: " % (ioaddrs[addr]), "N", "YN") is True:
      vicecommandline["-ds12c887rtcbase"] = addr
      ioaddrs[addr] = "ds12c887rtc"

  # -ds12c887rtchalted -> Set the RTC oscillator to 'halted'
  # -ds12c887rtcrunning -> Set the RTC oscillator to 'running'
  if "-ds12c887rtcrunning" in vicecommandline:
    ch = ttyio.inputchar("Set the RTC oscillator to {var:setupimagebbs.currentoption}[R]unning{/all} or [H]alted: ", "RH", "R")
  elif "-ds12c887rtchalted" in vicecommandline:
    ch = ttyio.inputchar("Set the RTC oscillator to [R]unning or {var:setupimagebbs.currentoption}[H]alted{/all}: ", "RH", "H")
  else:
    ch = ttyio.inputchar("Set the RTC oscillator to {var:setupimagebbs.currentoption}[R]unning{/all} or [H]alted: ", "RH", "R")

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

def rs232(args, **kwargs):
  area("vice: rs232/ip232")
  title("vice: rs232/ip232")
  dev = int(ttyio.inputchar("device [1-4]: ", "1234", "4"))
  vicecommandline["+rsuser"] = None
  vicecommandline["-rsdev%d" % (dev)] = "%s:%s" % (localhost, tcpsercommandline["-v"])
  vicecommandline["-rsdev%dip232" % (dev)] = None
  vicecommandline["-rsdev%dbaud" % (dev)] = tcpsercommandline["-s"] # 38400

  resultbuf = ""
  ttyio.echo("configured rsdev%d as ip232." % (dev))
  return (True, resultbuf)

def acia(args, **kwargs):
  area("vice")
  title("vice: acia")

  if ttyio.inputboolean("Enable the ACIA RS232 interface emulation (Swiftlink, Turbo32)? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y") is False:
    vicecommandline["+acia1"] = None
    for x in ["-acia1mode", "-acia1base", "-acia1irq", "-myaciadev", "-acia1"]:
      if x in vicecommandline:
        del vicecommandline[x]

    if "-acia1mode" in vicecommandline:
      del vicecommandline["-acia1mode"]
    if "-acia1base" in vicecommandline:
      del vicecommandline["-acia1base"]
    return True

  status = []

  # if acia1mode has already been set, use it, else "1" (swiftlink)
  d = vicecommandline["-acia1mode"] if "-acia1mode" in vicecommandline else 1
  ttyio.echo("acia.100: d=%r" % (d), level="debug")

  # normal=2400, swiftlink=38400, turbo32=230400. image can handle up to 38400
  options = [ "normal", "swiftlink", "turbo32" ]
  prompt = []
  o = ""
  for i in range(0, len(options)):
    if d == i:
      prompt.append("{var:setupimagebbs.currentoption}[%s] %s{/all}" % (chr(ord("A")+i), options[i]))
    else:
      prompt.append("[%s] %s" % (chr(ord("A")+i), options[i]))
    o += chr(ord("A")+i)

  promptbuf = "set the ACIA mode %s: [%s]? " % (" ".join(prompt), o)
  ch = ttyio.inputchar(promptbuf, o, chr(ord("A")+d))
  i = ord(ch) - ord("A")
  ttyio.echo("%s" % (options[i]))
  status.append("mode: %s" % (options[i]))

  vicecommandline["-acia1mode"] = i

  # $df00 is *not* supported by ml30 without a recompile
  ch = ttyio.inputchar("Base address of the ACIA cartridge {var:setupimagebbs.currentoption}[A] 0xDE00{/all} [B] 0xDF00: [AB]? ", "AB", "A")
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
    ttyio.echo("{var:setupimagebbs.currentoption}[A] None{/all}")
  else:
    ttyio.echo("[A] None")
  if default == "B":
    ttyio.echo("{var:setupimagebbs.currentoption}[B] NMI{/all}")
  else:
    ttyio.echo("[B] NMI")
  if default == "C":
    ttyio.echo("{var:setupimagebbs.currentoption}[C] IRQ{/all}")
  else:
    ttyio.echo("[C] IRQ")
  ch = ttyio.inputchar("Set the ACIA interrupt ([A] None, {var:setupimagebbs.currentoption}[B] NMI{/all}, [C] IRQ): [ABC]? ", "ABC", default)
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

  serialdev = int(vicecommandline["-myaciadev"]) if "-myaciadev" in vicecommandline else 4

  for s in range(1,4+1):
    if int(serialdev) == s:
      ttyio.echo("{var:setupimagebbs.currentoption}[%d] serial%d{/all}" % (serialdev, serialdev))
    else:
      ttyio.echo("[%d] serial %d" % (s, s))

  prompt = "acia device [1234]: "
  ch = ttyio.inputchar(prompt, "1234", "4")
  n = ord(ch) - ord("0")
  ttyio.echo("acia.100: n=%d" % (n))
  vicecommandline["-myaciadev"] = n
  ttyio.echo("serial%d" % (n))
  status.append("serial%d" % (n))
  # vicecommandline["-myaciadev"] = 3 # serial4
  vicecommandline["-acia1"] = None
  ttyio.echo("acia.120: status=%r" % (status), interpret=False)

  return (True, status) # (True, status) # "("+" ".join(status)+")")

def checktcpser(args, filename="tcpser"): # filename="/home/jam/tmp/tcpser-1.1.4/tcpser"):
  area("tcpser")
  title("tcpser: check")

  res = subprocess.run([filename, "-V"], capture_output=True, text=True)

  TCPSERVERSTRING = "(TCPSER) 1.1.5_alpha"

  # look for "invalid option -- 'V'" -- (-V added in 1.1.4, older versions will complain of invalid option)
  # ttyio.echo("%r" % (res.stderr))
  # ttyio.echo("stdout=%r" % (res.stdout))
  if res.stdout.find("invalid option -- 'V'") > -1 or res.stderr.find("invalid option -- 'V'") > -1:
    ttyio.echo("The version of tcpser installed is not compatible with imagebbs (>=1.1.4).")
    return False

  if res.stdout.find(TCPSERVERSTRING) > -1 or res.stderr.find(TCPSERVERSIONSTRING) > -1:
    ttyio.echo("The version of tcpser installed should be compatible with imagebbs")
    return True

def getvicefeatures(args:Namespace(), filename:str="x64sc"):
  area("vice - checking features")
  title("vice: check")

  res = subprocess.run([filename, "--features"], capture_output=True, text=True)

  features = {}
  for match in re.finditer(r"^HAVE_(\S+)\s+(yes|no)\s+(.*)", res.stdout, re.MULTILINE):
#    ttyio.echo("match.groups()=%r" % (match.groups(),))
    feature = match.group(1)
    value = True if match.group(2) == "yes" else False
    # description = match.group(3)
    features[feature] = value # (value, description)
#    ttyio.echo("features[%s]=%r" % (feature, value))
  return features

  if define == "RS232NET":
    ttyio.echo("{bold}%s: %s (%s){/all}" % (description, value, define))
    if value is False:
      ttyio.echo("RS232NET is not enabled.", level="error")
      return False
    else:
      ttyio.echo("RS232NET is enabled", level="success")
      return True
  elif define == "IPV6":
    ttyio.echo("{bold}%s: %s (%s){/all}" % (description, value, define))
    if value is False:
      ttyio.echo("IPV6 is not enabled.", level="error")
      return False
    else:
      ttyio.echo("IPV6 is enabled", level="success")
      return True

  return None

def checkvice(args):
  features = getvicefeatures(args)
  for check in [ "RS232NET", "IPV6" ]:
    if check in features and features[check] is True:
      pass

  if "RS232NET" in features and features["RS232NET"] is True:
    ttyio.echo("RS232NET is enabled.")
  else:
    ttyio.echo("RS232NET is not enabled.")
  if "IPV6" in features and features["IPV6"] is True:
    ttyio.echo("IPV6 is enabled.")
  else:
    ttyio.echo("IPV6 is not enabled.")


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

def tcpserphonebook(args):
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

def tcpser(args, **kwargs):
  area("tcpser")
  title("tcpser")

  # ttyio.echo("tcpser.120: vicecommandline=%r" % (vicecommandline), interpret=False)
  if ttyio.inputboolean("invert DCD pin? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN") is True:
    tcpsercommandline["-I"] = None

  acia1mode = vicecommandline["-acia1mode"] if "-acia1mode" in vicecommandline else None
  ttyio.echo("tcpser.120: acia1mode=%r" % (acia1mode), level="debug")

  if acia1mode == 1 or acia1mode == 2:
    speed = 38400
  else:
    speed = 2400

  tcpsercommandline["-s"] = ttyio.inputinteger("speed in bits per second (-s): ", speed)

  tcpsercommandline["-v"] = ttyio.inputinteger("tcp port for VICE RS232NET (-v): ", 25232)
  tcpsercommandline["-p"] = ttyio.inputstring("port or address:port (-p): ", "6400")

  tcpsercommandline["-i"] = ttyio.inputstring("modem init string (-i): at", "e0v0s0=1s2=27")

  title("tcpser: trace flags")

  traceflags = ""
  trace = []
  if ttyio.inputboolean("modem input (s) [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN") is True:
    traceflags += "s"
    trace += ["modem input"]
  if ttyio.inputboolean("modem output (S) [y{var:setupimagebbs.currentoption}N{/all}]: ", "N", "YN") is True:
    traceflags += "S"
    trace += ["modem output"]
  if ttyio.inputboolean("IP input (i) [y{var:setupimagebbs.currentoption}N{/all}]: ", "N", "YN") is True:
    traceflags += "i"
    trace += ["ip input"]
  if ttyio.inputboolean("IP output (I) [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN") is True:
    traceflags += "I"
    trace += ["ip output"]
  if len(traceflags) > 0:
    tcpsercommandline["-t"] = traceflags

  vocab = ["none", "fatal", "error", "warn", "info", "debug", "enter-exit", "all"]
  buf = ttyio.inputstring("Logging Level (-l): ", "all", completer=completeVocab(args, vocab), verify=verifyLoggingLevelName)
  level = None
  for i in range(0, len(vocab)):
    if vocab[i] == buf:
      level = i
      levelname = buf
      break

  if args is not None and args.debug is True:
    ttyio.echo("level=%r" % (level))

  tcpsercommandline["-l"] = level
  return (True, "logging: %s trace: %s speed: %s rs232net: %s port: %s" % (levelname, ttyio.oxfordcomma(trace), tcpsercommandline["-s"], tcpsercommandline["-v"], tcpsercommandline["-p"]))

def ramlink(args, **kwargs):
  area("vice")
  title("vice: ramlink")

  if ttyio.inputboolean("use ramlink? [y{var:setupimagebbs.currentoption}N{/all}]: ", "N") is False:
    vicecommandline["-ramlink"] = None
    if "+ramlink" in vicecommandline:
      del vicecommandline["+ramlink"]
    if "+ramlinkrtcsave" in vicecommandline:
      del vicecommandline["+rtcsave"]
    if "-ramlinksize" in vicecommandline:
      del vicecommandline["-ramlinksize":
    if "+ramlinksize" in vicecommandline:
      del vicecommandline["+ramlinksize"]
    if "-ramlinksize" in vicecommandline:
      del vicecommandline["-ramlinksize"]
    if "+ramlinkimagerw" in vicecommandline:
      del vicecommandline["+ramlinkimagerw"]
    if "-ramlinkimagerw" in vicecommandline:
      del vicecommandline["-ramlinkimagerw"]
    if "-ramlinkimage" in vicecommandline:
      del vicecommandline["-ramlinkimage"]
    return (True, "disabled")

  vicecommandline["+ramlink"] = None

  if ttyio.inputboolean("rtc save? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y") is True:
      vicecommandline["-rtcsave"] = None
      if "+rtcsave" in vicecommandline:
        del vicecommandline["+rtcsave"]
  else:
      vicecommandline["+rtcsave"] = None
      if "-rtcsave" in vicecommandline:
        del vicecommandline["-rtcsave"]

  if ttyio.inputboolean("allow write to ramlink image? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y") is True:
      vicecommandline["-ramlinkimagerw"] = None
      if "+ramlinkimagerw" in vicecommandline:
        del vicecommandline["+ramlinkimagerw"]
  else:
      vicecommandline["+ramlinkimagerw"] = None
      if "-ramlinkimagerw" in vicecommandline:
        del vicecommandline["-ramlinkimagerw"]

  vicecommandline["-ramlinksize"] = ttyio.inputinteger("ramlink size in MiB (0=Disabled): ", "1")

  vicecommandline["-cartramlink"] = inputfilename(args, "ramlink bin: ", "ramlink.bin")

  # handle pre-existing value!
  if ttyio.inputboolean("ramlink rtc save? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y") is True:
    vicecommandline["-ramlinkrtcsave"] = None
    if "+ramlinkrtcsave" in vicecommandline:
      del vicecommandline["+ramlinkrtcsave"]
  else:
    vicecommandline["+ramlinkrtcsave"] = None
    if "-ramlinkcrtsave" in vicecommandline:
      del vicecommandline["-ramlinkcrtsave"]

  # handle pre-existing value!
  ch = ttyio.inputchar("ramlinkmode ({var:setupimagebbs.currentoption}1=Normal{/all}, 0=Direct): ", "01", "1")
  if ch == "0":
    ttyio.echo("Direct")
  elif ch == "1":
    ttyio.echo("Normal")
  vicecommandline["-ramlinkmode"] = ch
  return True

def displaysync(args, **kwargs):
  area("vice")
  title("vice: display sync")
  sync = ttyio.inputchar("{var:setupimagebbs.currentoption}[N]TSC{/all} or [P]AL? ", "NP", "N")
  if sync == "N":
    ttyio.echo("NTSC")
    vicecommandline["-ntsc"] = None
    if "-pal" in vicecommandline:
      del vicecommandline["-pal"]
    resultbuf = "NTSC"
  elif sync == "P":
    ttyio.echo("PAL")
    vicecommandline["-pal"] = None
    if "-ntsc" in vicecommandline:
      del vicecommandline["-ntsc"]
    resultbuf = "PAL"
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
        ttyio.echo("{var:setupimagebbs.currentoption}[%s] %s{/all}" % (chr(char), v))
        default = chr(char)
      else:
        ttyio.echo("[%s] %s" % (chr(char), v))

      options += chr(char)

      menu[chr(char)] = k

      char += 1

    if default == "N":
      ttyio.echo("{var:setupimagebbs.currentoption}[N] None{/all}")
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
  if val < 8 or val > 11:
    ttyio.echo("ltk device number (%d) out of range." % (val))
    return False
  return True

def storage(args, **kwargs):
#  area("vice: storage")
#  title("vice: storage")

  useltk = setup["useltk"] if "useltk" in setup else True
  usecmd = setup["usecmd"] if "usecmd" in setup else False

  if useltk is True:
    ltk = ttyio.inputboolean("use ltk? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN")
  else:
    ltk = ttyio.inputboolean("use ltk? [y{bggray{white}N]: ", "N", "YN")
  if usecmd is True:
    cmd = ttyio.inputboolean("use cmd? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN")
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
      ch = vicecommandline["-ltkio"] = ttyio.inputchar("Set LTK IO page (0: $DE00, {var:setupimagebbs.currentoption}1: $DF00{/all}): ", "01", "1")
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
      if ttyio.inputboolean("Enable saving of RTC data to drive %d? [{var:setupimagebbs.currentoption}Y{/all}n]: " % (drivenumber), "Y", "YN") is True:
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

  if ttyio.inputboolean("restore default config before processing options? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y", "YN") is True:
    vicecommandline["-default"] = None
  return True

def saveonviceexit(args):
  area("vice")
  title("vice: save settings on vice exit")

  if ttyio.inputboolean("save vice settings on exit from vice? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y") is True:
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
  
  if ttyio.inputboolean("save setup data? [{var:setupimagebbs.currentoption}Y{/all}n]: ", "Y") is False:
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
    ttyio.echo("{var:setupimagebbs.currentoption}[A] error message, detatch all involved carts{/all}")
  else:
    ttyio.echo("[A] error message, detatch all involved carts")

  if default == "B":
    ttyio.echo("{var:setupimagebbs.currentoption}[B] error message, detach most recent involved cart{/all}")
  else:
    ttyio.echo("[B] error message, detach most recent involved cart")
  
  if default == "C":
    ttyio.echo("{var:setupimagebbs.currentoption}[C] warning in log, bitwise-and valid return values{/all}")
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

    parser.add_argument("--storage", action="store", choices=["ltk", "cmd", "mix"], dest="storage")
    parser.add_argument("--ramlink", action="store_true", dest="ramlink")
    parser.add_argument("--basedir", action="store", dest="basedir", default="~jam/projects/gfd3/")
    args = parser.parse_args()
    # ttyio.echo("args=%r" % (args), level="debug")

    locale.setlocale(locale.LC_ALL, "")

    terminalwidth = ttyio.getterminalwidth()

    ttyio.echo("{f6:5}{curpos:%d,0}" % (ttyio.getterminalheight()-3))
    initscreen(bottommargin=1)

    area("setup image bbs v3.0")

    ttyio.setvariable("menu.boxcharcolor", "{blue}")
    ttyio.setvariable("menu.backgroundcolor", "{bglightblue}")
    ttyio.setvariable("menu.shadowbackgroundcolor", "{bgblue}")
    ttyio.setvariable("menu.cursorcolor", "{bglightgray}{blue}")
    ttyio.setvariable("menu.boxcolor", "{bgblack}{green}")
    ttyio.setvariable("menu.itemcolor", "{bglightblue}{blue}")
    ttyio.setvariable("menu.titlecolor", "{black}{bglightgray}")
    ttyio.setvariable("menu.promptcolor", "{white}{bgblack}")
    ttyio.setvariable("menu.inputcolor", "{white}{bgblack}")
    ttyio.setvariable("menu.disableditemcolor", "{black}{bgdarkgray}")

    ttyio.setvariable("setupimagebbs.currentoption", "{bggray}{white}")

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
      { "name": "acia",          "callback": acia,            "label": "acia setup", "requires":()},
      { "name": "tcpser",        "callback": tcpser,          "label": "tcpser parameters", "requires":("acia",)},
      { "name": "rs232",         "callback": rs232,         "label": "rs232/ip232", "requires": ("tcpser", "acia",)},
      { "name": "drivesound",    "callback": drivesound,      "label": "drive sound"},
      { "name": "displaysync",   "callback": displaysync,     "label": "display"},
#      { "name": "clock",         "callback": "clock",         "label": "rtc (real-time clock)", "requires": ("storage",)},
#      { "name": "storage",       "callback": "storage",       "label": "storage"},
#      { "name": "keyboard",      "callback": "keyboard",      "label": "keyboard settings"},
      { "name": "ramlink",       "callback": ramlink,       "label": "ramlink"},
      { "name": "sound",         "callback": sound,         "label": "sound"}
    ]

    menu = Menu("image bbs v3 setup", menuitems)
    menu.run()

#      res = handlemenu(args, menuitems, "setup: ")
#      ttyio.echo("main.100: res=%r" % (res,))
#      if res is True:
#        ttyio.echo("OK", level="success")
#        continue
#      elif res is False:
#        ttyio.echo("FAILED", level="error")
#        if ttyio.inputboolean("proceed anyway? [yN]: ", "N", "YN") is False:
#          done = True
#      elif res is None:
#        done = True
#      elif type(res) == tuple:
#        ttyio.echo("tuple")
#      else:
#        ttyio.echo("??? res=%r" % (res,))

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
