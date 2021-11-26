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
import subprocess

import ttyio5 as ttyio
import bbsengine5 as bbsengine

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

#def title(title:str, titlecolor:str="{bgray}{white}", hrcolor:str="{white}", hrchars:str="{acs:hline}", llcorner="{acs:llcorner}", lrcorner="{acs:lrcorner}", ulcorner="{acs:ulcorner}", urcorner="{acs:urcorner}", width=None):
#  if width is None:
#    width = ttyio.getterminalwidth()-2
#
#  ttyio.echo("{/all}%s%s{acs:hline:%s}%s" % (hrcolor, ulcorner, width, urcorner), end="")
#  ttyio.echo("{f6}{white}{acs:vline}{bggray}{white}%s{/all}{white}{acs:vline}{/all}" % (title.center(width)), end="")
#  ttyio.echo("{f6}{white}%s{acs:hline:%s}%s{/all}" % (llcorner, width, lrcorner))
#  return


def area(buf):
  width = ttyio.getterminalwidth()
  updatebottombar("{var:setupimagebbs.areacolor} %s {/all}" % (buf.ljust(width-2, " ")))
  return

def sound(args, **kwargs):
  bbsengine.setarea("sound")
  status = []
  if ttyio.inputboolean("enable sound? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN") is False:
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
  soundsync = vicecommandline["-soundsync"] if "-soundsync" in vicecommandline else "0"
  prompt = "soundsync "
  if soundsync == "0":
    prompt += "{var:engine.currentoptioncolor}0: system{/all} "
  else:
    prompt += "0: system "
  if soundsync == "1":
    prompt += "{var:engine.currentoptioncolor}1: mono{/all} "
  else:
    prompt += "1: mono "
  if soundsync == "2":
    prompt += "{var:engine.currentoptioncolor}2: stereo{/all}"
  else:
    prompt += "2: stereo"
  prompt += ": "
  ch = ttyio.inputchar(prompt, "012", soundsync)
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
  soundvolume = vicecommandline["-soundvolume"] if "-soundvolume" in vicecommandline else "70"
  vol = ttyio.inputinteger("soundvolume (0-100): ", soundvolume)
  vicecommandline["-soundvolume"] = vol
  status.append("vol: %s" % (vol))

  # -sounddev
  sounddev = vicecommandline["-sounddev"] if "-sounddev" in vicecommandline else "pulse"

  ttyio.echo("sound.100: sounddev=%r" % (sounddev), level="debug")

  opts = []
  if sounddev == "pulse":
    opts.append("{var:engine.currentoptioncolor}[P]ulse{/all}")
  else:
    opts.append("[P]ulse")
  if sounddev == "alsa":
    opts.append("{var:engine.currentoptioncolor}[A]LSA{/all}")
  else:
    opts.append("[A]LSA")
  if sounddev == "sdl":
    opts.append("{var:engine.currentoptioncolor}[S]DL{/all}")
  else:
    opts.append("[S]DL")
  if sounddev == "dummy":
    opts.append("{var:engine.currentoptioncolor}[D]ummy{/all}")
  else:
    opts.append("[D]ummy")
  dev = ttyio.inputchar("%s: " % (" ".join(opts)), "PASD", sounddev)
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

  return (True, status)

def truedrive(args, **kwargs):
  bbsengine.setarea("vice: truedrive")
  bbsengine.title("vice: truedrive")
  if "-truedrive" in vicecommandline:
    defaultvalue = "Y"
  elif "+truedrive" in vicecommandline:
    defaultvalue = "N"
  else:
    defaultvalue = "Y"

  if defaultvalue == "Y":
    ch = ttyio.inputboolean("truedrive? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN")
  else:
    ch = ttyio.inputboolean("truedrive? [y{var:engine.currentoptioncolor}N{/all}]: ", "N", "YN")

  if ch is True:
    if "+truedrive" in vicecommandline:
      del vicecommandline["+truedrive"]
    vicecommandline["-truedrive"] = None
  else:
    if "-truedrive" in vicecommandline:
      del vicecommandline["-truedrive"]
    vicecommandline["+truedrive"] = None

def drivesound(args, **kwargs):
  bbsengine.setarea("vice: drivesound")
  bbsengine.title("vice: drivesound")

  if ttyio.inputboolean("Enable sound emulation of disk drives? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN") is True:
    volume = ttyio.inputinteger("drive sound volume? [0-100]: ", 70)
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
  bbsengine.setarea("vice: clock")
  bbsengine.title("clock")
# clock1 = ds12c887rtc(args)
#  clock1 =  ttyio.inputboolean("use ds12c887rtc? [{bggray}{white}Y{/all}n]: ", "Y", "YN")
#  if clock1 is False:
  clock2 = ttyio.inputboolean("use cmd fd-4000 RTC? [y{var:engine.currentoptioncolor}N{/all}]: ", "N", "YN")
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
  bbsengine.setarea("system: check for 'localhost' in dns")
  ttyio.echo("testing for localhost: ", flush=True, end="")
  try:
    res = socket.gethostbyname("localhost")
  except:
    ttyio.echo("dns check for 'localhost' failed, reverting to ipv4 address 127.0.0.1", level="warn")
    return "127.0.0.1"
  else:
    ttyio.echo("dns check for 'localhost' passed", level="success")
    return "localhost"

#def verifyFileExistsReadable(args, filename):
#  filename = os.path.expanduser(filename)
#  filename = os.path.expandvars(filename)
#  if args is not None and args.debug is True:
#    ttyio.echo("args=%r filename=%r" % (args, filename))
#
#  if os.access(filename, os.R_OK) is True and os.path.isfile(filename) is True:
#    return True
#  return False

#def inputfilename(args, prompt, default, verify=verifyFileExistsReadable, **kwargs):
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
  if ttyio.inputboolean("use settings for 'gfd3'? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN") is True:
    vicecommandline["-10"] = os.path.join(args.basedir, "drive10.d81")
    vicecommandline["-11"] = os.path.join(args.basedir, "drive11.d81")
    vicecommandline["-drive10type"] = "1581"
    vicecommandline["-drive11type"] = "1581"
    vicecommandline["-ltkimage0"] = os.path.join(args.basedir, "drive8-0.dlk")
    vicecommandline["-ltkimage1"] = os.path.join(args.basedir, "drive8-1.dlk")
    vicecommandline["-ltkimage2"] = os.path.join(args.basedir, "drive8-2.dlk")
  return True

def keyboard(args, **kwargs):
  bbsengine.setarea("vice: keyboard")
  bbsengine.title("keyboard")

  keyboards = ("0: Symbpolic", "1: Positional", "2: symbolic (user)", "3: positional (user)")
  ch = ttyio.inputchar("Specify index of keymap file ({var:engine.currentoptioncolor}0:symbolic{/all}, 1:positional, 2:symbolic (user), 3:positional (user))? [0123]: ","0123", "0")
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
  bbsengine.setarea("vice: cmd4000")
  bbsengine.title("device 9 cmd 4000")
  if ttyio.inputboolean("enable cmd fd-4000 on device 9? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN") is True:
    vicecommandline["-dos4000"] = bbsengine.inputfilename(args, "dos4000 filename: ", os.path.join(args.basedir, "cmd-fd-4000-dos-v1.40-fd-350022.bin"), verify=bbsengine.verifyFileExistsReadable)
    vicecommandline["-drive9type"] = "4000"
    if ttyio.inputboolean("enable drive 9 rtc save? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN") is True:
      vicecommandline["-drive9rtcsave"] = None
    else:
      vicecommandline["+drive9rtcsave"] = None

def inputioaddr(args, optionslist:list, currentvalue:str, defaultvalue:str):
  pass

def ds12c887rtc(args, **kwargs):
  bbsengine.setarea("vice: ds12c887rtc")
  bbsengine.title("ds12c887rtc")
  if "-ds12c887rtc" in vicecommandline:
    ch = ttyio.inputboolean("Enable DS12C887RTC? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN")
  elif "+ds12c887rtc" in vicecommandline:
    ch = ttyio.inputboolean("Enable DS12C887RTC? [y{var:engine.currentoptioncolor}N{/all}]: ", "N", "YN")
  else:
    ch = ttyio.inputboolean("Enable DS12C887RTC? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN")

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
    ch = ttyio.inputboolean("Enable saving of the DS12C887RTC data when changed? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN")
  elif "+ds12c887rtcsave" in vicecommandline:
    ch = ttyio.inputboolean("Enable saving of the DS12C887RTC data when changed? [y{var:engine.currentoptioncolor}N{/all}]: ", "N", "YN")
  else:
    ch = ttyio.inputboolean("Enable saving of the DS12C887RTC data when changed? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN")

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
      menu.append("{var:engine.currentoptioncolor}[%s] %s{/all}" % (chr(ch), addresschoices[i]))
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
    if ttyio.inputboolean("that address is already used for %s. proceed? [y{var:engine.currentoptioncolor}N{/all}]: " % (ioaddrs[addr]), "N", "YN") is True:
      vicecommandline["-ds12c887rtcbase"] = addr
      ioaddrs[addr] = "ds12c887rtc"

  # -ds12c887rtchalted -> Set the RTC oscillator to 'halted'
  # -ds12c887rtcrunning -> Set the RTC oscillator to 'running'
  if "-ds12c887rtcrunning" in vicecommandline:
    ch = ttyio.inputchar("Set the RTC oscillator to {var:engine.currentoptioncolor}[R]unning{/all} or [H]alted: ", "RH", "R")
  elif "-ds12c887rtchalted" in vicecommandline:
    ch = ttyio.inputchar("Set the RTC oscillator to [R]unning or {var:engine.currentoptioncolor}[H]alted{/all}: ", "RH", "H")
  else:
    ch = ttyio.inputchar("Set the RTC oscillator to {var:engine.currentoptioncolor}[R]unning{/all} or [H]alted: ", "RH", "R")

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
  bbsengine.setarea("vice: rs232/ip232")
  bbsengine.title("vice: rs232/ip232")
  dev = ttyio.inputinteger("device [1-{var:engine.currentoptioncolor}4{/all}]: ", 4)
  vicecommandline["+rsuser"] = None
  vicecommandline["-rsdev%d" % (dev)] = "%s:%s" % (localhost, tcpsercommandline["-v"])
  ip232 = ttyio.inputboolean("enable ip232? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y")
  vicecommandline["-rsdev%dip232" % (dev)] = ip232
  baud = ttyio.inputinteger("baud rate: ", tcpsercommandline["-s"]) # 38400
  vicecommandline["-rsdev%dbaud" % (dev)] = baud

  resultbuf = "[dev: %d] [ip232: %s] [baud: %d]" % (dev, ip232, baud)

#  ttyio.echo("configured rsdev%d as ip232." % (dev))
  return (True, resultbuf)

def acia(args, **kwargs):
  global ioaddrs

  bbsengine.setarea("vice: acia")
  bbsengine.title("vice: acia")

  if ttyio.inputboolean("Enable the ACIA RS232 interface emulation (Swiftlink, Turbo232)? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y") is False:
    vicecommandline["+acia1"] = None
    for x in ["-acia1mode", "-acia1base", "-acia1irq", "-myaciadev", "-acia1"]:
      if x in vicecommandline:
        del vicecommandline[x]

    return True

  status = []

  # if acia1mode has already been set, use it, else "1" (swiftlink)
  acia1mode = vicecommandline["-acia1mode"] if "-acia1mode" in vicecommandline else 1
  ttyio.echo("acia.100: acia1mode=%r" % (acia1mode), level="debug")

  # normal=2400, swiftlink=38400, turbo32=230400. image can handle up to 38400
  options = [ "normal", "swiftlink", "turbo232" ]
  prompt = []
  o = ""
  for i in range(0, len(options)):
    if acia1mode == i:
      prompt.append("{var:engine.currentoptioncolor}[%s] %s{/all}" % (chr(ord("A")+i), options[i]))
    else:
      prompt.append("[%s] %s" % (chr(ord("A")+i), options[i]))
    o += chr(ord("A")+i)

  promptbuf = "set the ACIA mode %s: [%s]? " % (" ".join(prompt), o)
  ch = ttyio.inputchar(promptbuf, o, chr(ord("A")+acia1mode))
  i = ord(ch) - ord("A")
  ttyio.echo("%s" % (options[i]))
  status.append("mode: %s" % (options[i]))

  vicecommandline["-acia1mode"] = i

  # 0xDF00 is *not* supported by image ml30 without a recompile. 0xDF00 is used by LTK
  ioaddr = vicecommandline["-acia1base"] if "-acia1base" in vicecommandline else "0xDE00"
  ttyio.echo("ioaddr=%s" % (ioaddr), level="debug")
  if ioaddr == "0xDF00":
    ttyio.echo("Warning: Image BBS 3.0 does not support 0xDF00 for the ACIA Cart", level="warn")

  prompt = "Base address of the ACIA cartridge "
  if ioaddr == "0xDE00":
    prompt += "{var:engine.currentoptioncolor}[A] 0xDE00{/all} [B] 0xDF00"
    default = "A"
  elif ioaddr == "0xDF00":
    prompt += "[A] 0xDE00 {var:engine.currentoptioncolor}[B] 0xDF00{/all}"
    default = "A"

  prompt += ": [AB]? "
  ch = ttyio.inputchar(prompt, "AB", default)
  if ch == "A":
    ttyio.echo("0xDE00")
    vicecommandline["-acia1base"] = "0xDE00"
    ioaddrs["0xDE00"] = "acia1"
    status.append("io: 0xDE00")
  else:
    ttyio.echo("0xDF00")
    vicecommandline["-acia1base"] = "0xDF00"
    ioaddrs["0xDF00"] = "acia1"
    status.append("io: 0xDF00")
    ttyio.echo("Warning: Image BBS 3.0 does not support address 0xDF00 for the ACIA Cart", level="warn")


  prompt = "Set the ACIA interrupt ("
  acia1irq = vicecommandline["-aciairq"] if "-aciairq" in vicecommandline else "1"
  if acia1irq == "0":
    prompt += "{var:engine.currentoptioncolor}[0] None{/all}"
  else:
    prompt += "[0] None"

  if acia1irq == "1":
    prompt += " {var:engine.currentoptioncolor}[1] NMI{/all}"
  else:
    prompt += " [1] NMI"

  if acia1irq == "2":
    prompt += " {var:engine.currentoptioncolor}[2] IRQ{/all}"
  else:
    prompt += " [2] IRQ"
  prompt += ") [012]: "

#  ttyio.echo("Warning: Image BBS 3.0 does not support 0xDF00 for the ACIA Cart", level="warn")
#  ttyio.echo("acia1mode=%r" % (str(acia1mode)), level="debug")
  ch = ttyio.inputchar(prompt, "012", str(acia1mode))
  if ch == "0":
    vicecommandline["-acia1irq"] = 0
    ttyio.echo("0: None")
    status.append("interrupts: None")
  elif ch == "1":
    vicecommandline["-acia1irq"] = 1
    ttyio.echo("1: NMI")
    status.append("interrupts: NMI")
  elif ch == "2":
    ttyio.echo("2: IRQ")
    vicecommandline["-acia1irq"] = 2
    status.append("interrupts: IRQ")

  serialdev = int(vicecommandline["-myaciadev"]) if "-myaciadev" in vicecommandline else 4

  for s in range(1,4+1):
    if int(serialdev) == s:
      ttyio.echo("{var:engine.currentoptioncolor}[%d] serial%d{/all}" % (serialdev, serialdev))
    else:
      ttyio.echo("[%d] serial %d" % (s, s))

  prompt = "acia device [1234]: "
  ch = ttyio.inputchar(prompt, "1234", "4")
  n = ord(ch) - ord("0")
  ttyio.echo("acia.100: n=%d" % (n), level="debug")
  vicecommandline["-myaciadev"] = n
  ttyio.echo("serial%d" % (n))
  status.append("serial%d" % (n))
  # vicecommandline["-myaciadev"] = 3 # serial4
  vicecommandline["-acia1"] = None
  ttyio.echo("acia.120: status=%r" % (status), interpret=False, level="debug")

  acia1base = vicecommandline["-acia1base"] if "-acia1base" in vicecommandline else "0xDE00"

  if acia1base == "0xDF00":
    return (False, status)
  return (True, status) # (True, status) # "("+" ".join(status)+")")

def checktcpser(args, filename="tcpser"): # filename="/home/jam/tmp/tcpser-1.1.4/tcpser"):
  bbsengine.setarea("tcpser")
  bbsengine.title("tcpser: check")

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
  bbsengine.setarea("vice - checking features")
#  title("vice: check")

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
  bbsengine.setarea("checkvice")
  bbsengine.title("check vice features")

  ttyio.echo("checkvice: ", end="", flush=True)
  features = getvicefeatures(args)
  ttyio.echo("OK")
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
  bbsengine.setarea("tcpser")
  bbsengine.title("tcpser")

  # ttyio.echo("tcpser.120: vicecommandline=%r" % (vicecommandline), interpret=False)
  if ttyio.inputboolean("invert DCD pin? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN") is True:
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

  bbsengine.title("tcpser: trace flags")

  traceflags = ""
  trace = []
  if ttyio.inputboolean("modem input (s) [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN") is True:
    traceflags += "s"
    trace += ["modem input"]
  if ttyio.inputboolean("modem output (S) [y{var:engine.currentoptioncolor}N{/all}]: ", "N", "YN") is True:
    traceflags += "S"
    trace += ["modem output"]
  if ttyio.inputboolean("IP input (i) [y{var:engine.currentoptioncolor}N{/all}]: ", "N", "YN") is True:
    traceflags += "i"
    trace += ["ip input"]
  if ttyio.inputboolean("IP output (I) [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN") is True:
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
  bbsengine.setarea("vice: ramlink")
  bbsengine.title("vice: ramlink")

  if "+ramlink" in vicecommandline:
    useramlink = True
    if "-ramlink" in vicecommandline:
      del vicecommandline["-ramlink"]
    prompt = "use ramlink? [{var:engine.currentoptioncolor}Y{/all}n]: "
    default = "Y"
    vicecommandline["+ramlink"] = None
  else:
    useramlink = False
    if "+ramlink" in vicecommandline:
      del vicecommandline["+ramlink"]
    prompt = "use ramlink? [y{var:engine.currentoptioncolor}N{/all}]: "
    default = "N"

  if ttyio.inputboolean(prompt, default) is False:
    vicecommandline["-ramlink"] = None
    for x in ["+ramlink", "+ramlinkrtcsave", "-ramlinksize", "+ramlinksize", "-ramlinkimage", "-ramlinkimagerw", "+ramlinkimagerw", "-cartramlink"]:
      if x in vicecommandline:
        del vicecommandline[x]
    return (True, "disabled")

  description = []

  size = ttyio.inputinteger("ramlink size in MiB (0=Disabled): ", 16)
  if size == 0:
    return (True, "disabled")

  vicecommandline["-ramlinksize"] = size
  description.append("[size: %s]" % (bbsengine.pluralize(size, "megabyte", "megabytes")))

  if ttyio.inputboolean("allow write to ramlink image? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y") is True:
      vicecommandline["-ramlinkimagerw"] = None
      description.append("[write image: Yes]")
      if "+ramlinkimagerw" in vicecommandline:
        del vicecommandline["+ramlinkimagerw"]
  else:
      vicecommandline["+ramlinkimagerw"] = None
      if "-ramlinkimagerw" in vicecommandline:
        del vicecommandline["-ramlinkimagerw"]
      description.append("[write image: No]")

  vicecommandline["-cartramlink"] = bbsengine.inputfilename(args, "cart ramlink bin: ", os.path.join(args.basedir, "ramlink.bin"), verify=bbsengine.verifyFileExistsReadable)

  vicecommandline["-ramlinkimage"] = bbsengine.inputfilename(args, "ramlink image: ", os.path.join(args.basedir, "ramlink.img"), verify=bbsengine.verifyFileExistsReadableWritable)

  # handle pre-existing value!
  if ttyio.inputboolean("ramlink rtc save? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y") is True:
    vicecommandline["-ramlinkrtcsave"] = None
    if "+ramlinkrtcsave" in vicecommandline:
      del vicecommandline["+ramlinkrtcsave"]
    description.append("[rtc save: Yes]")
  else:
    vicecommandline["+ramlinkrtcsave"] = None
    if "-ramlinkcrtsave" in vicecommandline:
      del vicecommandline["-ramlinkrtcsave"]
    description.append("[rtc save: No]")

  # handle pre-existing value!
  ramlinkmode = vicecommandline["-ramlinkmode"] if "-ramlinkmode" in vicecommandline else "1"
  prompt = "ramlinkmode ("
  if ramlinkmode == "1":
    prompt += "{var:engine.currentoptioncolor}1=Normal{/all}, 0=Direct"
  else:
    prompt += "1=Normal, {var:engine.currentoptioncolor}0=Direct{/all}"
  prompt += "): "
  ch = ttyio.inputchar(prompt, "01", ramlinkmode)
  if ch == "0":
    ttyio.echo("Direct")
    description.append("[mode: direct]")
  elif ch == "1":
    ttyio.echo("Normal")
    description.append("[mode: normal]")

  vicecommandline["-ramlinkmode"] = ch
  return (True, description)

def displaysync(args, **kwargs):
  bbsengine.setarea("vice: display")
  bbsengine.title("vice: display")
  sync = ttyio.inputchar("{var:engine.currentoptioncolor}[N]TSC{/all} or [P]AL? ", "NP", "N")
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
# 1540: CBM 1540,
# 1541: CBM 1541,
# 1542: CBM 1541-II,
# 1570: CBM 1570,
# 1571: CBM 1571,
# 1581: CBM 1581,
# 2000: CMD FD-2000,
# 4000: CMD FD-4000,
# 4844: CMD HD,
# 2031: CBM 2031,
# 2040: CBM 2040,
# 3040: CBM 3040,
# 4040: CBM 4040,
# 1001: CBM 1001,
# 8050: CBM 8050,
# 8250: CBM 8250

#    types = {
#        "1001":    ("CBM 1001", StorageDeviceCBM),
#        "1540":    ("CBM 1540", StorageDeviceCBM),
#        "1541":    ("CBM 1541", StorageDeviceCBM),
#        "1542":    ("CBM 1541-II", StorageDeviceCBM),
#        "1570":    ("CBM 1570", StorageDeviceCBM),
#        "1571":    ("CBM 1571", StorageDeviceCBM),
#        "1581":    ("CBM 1581", StorageDeviceCBM),
#        "2031":    ("CBM 2031", StorageDeviceCBM),
#        "8050":    ("CBM 8050", StorageDeviceCBM),
#        "8250":    ("CBM 8250", StorageDeviceCBM),
#        "LTK":     ("Lt. Kernal", StorageDeviceLTK),
#        "2000":    ("CMD FD-2000", StorageDeviceCMD),
#        "4000":    ("CMD FD-4000", StorageDeviceCMD),
#        "4844":    ("CMD HD", StorageDeviceCMD)
#    }

    labels = {
        "1001":    "CBM 1001",
        "1540":    "CBM 1540",
        "1541":    "CBM 1541",
        "1542":    "CBM 1541-II",
        "1570":    "CBM 1570",
        "1571":    "CBM 1571",
        "1581":    "CBM 1581",
        "2031":    "CBM 2031",
        "8050":    "CBM 8050",
        "8250":    "CBM 8250",
        "LTK":     "Lt. Kernal",
        "2000":    "CMD FD-2000",
        "4000":    "CMD FD-4000",
        "4844":    "CMD HD",
    }

#    if "-dos4000" in vicecommandline and vicecommandline["-dos4000"] is not None:
#      # types["2000"] = "CMD FD-2000"
#      types["4000"] = "CMD FD-4000"

    if args.debug is True:
      ttyio.echo("drivetype.100: oldvalue=%r" % (oldvalue))

    default = "N"
    options = "N"
    menu = {}
    char = ord("A")
    for k, v in labels.items():
      label = v
      if k == oldvalue:
        ttyio.echo("{var:engine.currentoptioncolor}[%s] %s{/all}" % (chr(char), label))
        default = chr(char)
      else:
        ttyio.echo("[%s] %s" % (chr(char), label))

      options += chr(char)

      menu[chr(char)] = k

      char += 1

    if default == "N":
      ttyio.echo("{var:engine.currentoptioncolor}[N] None{/all}")
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
    ttyio.echo("ltk device number (%d) out of range." % (val), level="error")
    return False
  return True

cbmtypes = {
  "1541":    "CBM 1541",
  "1542":    "CBM 1541-II",
  "1570":    "CBM 1570",
  "1571":    "CBM 1571",
  "1581":    "CBM 1581",
  "2031":    "CBM 2031",
  "8050":    "CBM 8050",
  "8250":    "CBM 8250"
}

class StorageDevice(object):
  def __init__(self, args, number, **kwargs):
    self.args = args

    self.number = number
    self.type = None
    self.hasrtc = False
    self.savertc = False
    self.usertc = False
    self.images = []

 #   if "data" in kwargs:
 #     d = kwargs["data"]
 #     for a in [ "number", "type", "rtc", "savertc", "cart", "fallbacktype", "images" ]:
 #       if a in d:
 #         setattr(self, a, d[a])

  def __str__(self):
    buf = "#% d %s" % (self.number, self.type)
    if self.usertc is True:
      buf += " rtc"
      if self.savertc is True:
        buf += ": saved"
    if self.cart is not None:
      buf += " cart: %s" % (self.cart)

    return buf

#    return "#%d type: %s rtc: %s (%s) cart: %s fallbacktype: %s" % (self.number, self.type, self.rtc, self.savertc, self.cart, self.fallbacktype)

  def edit(self):
    self.type = drivetype(self.args, self.number)
    if self.type in ("4000", "4844", "RAMLINK", "2000"):
      if self.hasrtc is True:
        prompt = "use rtc? [{var:engine.currentoptioncolor}Y{/all}n]: "
        currentoption = "Y"
      else:
        prompt = "use rtc? [y{var:engine.currentoptioncolor}N{/all}]: "
        currentoption = "N"
      self.usertc = ttyio.inputboolean(prompt, currentoption)

      if self.savertc is True:
        prompt = "save rtc? [{var:engine.currentoptioncolor}Y{/all}n]: "
        currentoption = "Y"
      else:
        prompt = "save rtc? [y{var:engine.currentoptioncolor}N{/all}]: "
        currentoption = "N"
      self.savertc = ttyio.inputboolean(prompt, currentoption)
      # add device to rtc list
    return

class StorageDeviceLTK(StorageDevice):
  def __init__(self, args, number, drivetype="LTK"):
    super().__init__(args, number, drivetype="LTK") # , data:dict={}, **kwargs)
    self.type = drivetype
    self.hasrtc = False
    self.fallbacktype = None
    self.args = args
#    print("self.args=%r" % (self.args))
  def build(self):
    vicecommandline["-cartcrt"] = self.cartcrt
    vicecommandline["-ltkimage0"] = self.ltkimage0
    vicecommandline["-ltkimage1"] = self.ltkimage1
    vicecommandline["-ltkimage2"] = self.ltkimage2
    vicecommandline["-ltkport"] = self.ltkport
    return

  def edit(self):
      cartcrt = vicecommandline["-cartcrt"] if "-cartcrt" in vicecommandline else os.path.join(self.args.basedir, "ltk.crt")
      self.cartcrt = bbsengine.inputfilename(self.args, "-cartcrt: ", cartcrt, verify=bbsengine.verifyFileExistsReadable)

      ltkimage0 = vicecommandline["-ltkimage0"] if "-ltkimage0" in vicecommandline else os.path.join(self.args.basedir, "drive8-0.dlk")
      ltkimage1 = vicecommandline["-ltkimage1"] if "-ltkimage1" in vicecommandline else os.path.join(self.args.basedir, "drive8-1.dlk")
      ltkimage2 = vicecommandline["-ltkimage2"] if "-ltkimage2" in vicecommandline else os.path.join(self.args.basedir, "drive8-2.dlk")
      self.ltkimage0 = bbsengine.inputfilename(self.args, "-ltkimage0: ", ltkimage0, verify=bbsengine.verifyFileExistsReadableWritable)
      self.ltkimage1 = bbsengine.inputfilename(self.args, "-ltkimage1: ", ltkimage1, verify=bbsengine.verifyFileExistsReadableWritable)
      self.ltkimage2 = bbsengine.inputfilename(self.args, "-ltkimage2: ", ltkimage2, verify=bbsengine.verifyFileExistsReadableWritable)

      ltkport = vicecommandline["-ltkport"] if "-ltkport" in vicecommandline else 0
      self.ltkport = ttyio.inputinteger("Set LTK port number (0..15): ", ltkport, verify=verifyLTKPortInRange)
      vicecommandline["-ltkport"] = self.ltkport

      ltkio = vicecommandline["-ltkio"] if "-ltkio" in vicecommandline else "1"
      prompt = "Set LTK IO page ("
      if ltkio == "0":
        prompt += "{var:engine.currentoptioncolor}0: 0xDE00{/all}, 1: 0xDF00"
      elif ltkio == "1":
        prompt += "0: 0xDE00, {var:engine.currentoptioncolor}1: 0xDF00{/all}"
      prompt += "): "
      ch = vicecommandline["-ltkio"] = ttyio.inputchar(prompt, "01", "1")

      ttyio.echo("ch=%r" % (ch), level="debug")

      if ch == "1":
        ttyio.echo("1: 0xDF00")
        ioaddrs["0xDF00"] = "ltkio"
        if "0xDE00" in ioaddrs and ioaddrs["0xDE00"] == "ltkio":
          del ioaddrs["0xDE00"]
      elif ch == "0":
        ttyio.echo("0: 0xDE00")
        ttyio.echo("{f6}Warning: Using 0xDE00 for the LTK IO address is not supported by Image BBS 3.0.{f6}", level="warn")
        ioaddrs["0xDE00"] = "ltkio"
        if "0xDF00" in ioaddrs and ioaddrs["0xDF00"] == "ltkio":
          del ioaddrs["0xDF00"]
      vicecommandline["-ltkio"] = ch

      if self.number > 11:
        ttyio.echo("fallback device disabled, #% d is greater than 11." % (self.number))
        return

      if ttyio.inputboolean("use fallback device? [yN]: ", "N") is True:
        self.fallbacktype = ttyio.inputstring("fallback device (cbm only): ", "1581")
        vicecommandline["-drive%dtype" % (self.number)] = self.fallbacktype
        d = vicecommandline["-%d" % (self.number)] if "-%d" % (self.number) in vicecommandline else ""
        image = bbsengine.inputfilename(self.args, "fallback image name: ", d)
        if image is not None:
          vicecommandline["-%d" % (self.number)] = image
#          ttyio.echo("-%d set" % (self.number))

      ttyio.echo("setting -kernal to 'kernal'")
      vicecommandline["-kernal"] = "kernal"
      return

  add = edit

  def __str__(self):
    buf = "#% d %s" % (self.number, self.type)
#    if self.cartcrt is not None:
#      buf += " cart: %s" % (self.cartcrt)
    if self.fallbacktype is not None:
      buf += " fallback: %s" % (self.fallbacktype)
    if "-ltkio" in vicecommandline:
      ltkio = vicecommandline["-ltkio"]
      if ltkio == "0":
        buf += " ltkio: 0xDE00"
      elif ltkio == "1":
        buf += " ltkio: 0xDF00"
      else:
        buf += " ltkio: ERROR"
    if self.ltkport is not None:
      buf += " ltkport: %d" % (self.ltkport)

    return buf

class StorageDeviceCBM(StorageDevice):
  def __init__(self, args, number, drivetype="CBM"):
    super().__init__(args, number, drivetype="CBM") # , data:dict={}, **kwargs)
    self.type = drivetype
    self.hasrtc = False
    self.number = number
    self.args = args
    self.image = None

  def __str__(self):
    buf = "#% d %s" % (self.number, self.type)
    if self.image is not None:
      buf += " image: %s" % (self.image)
    return buf

  def add(self):
    self.image = bbsengine.inputfilename(self.args, "image name: ", self.image)

  def edit(self):
    for k, v in cbmtypes.items():
      ttyio.echo("[%s] %s" % (k, v))
    t = ttyio.inputstring("type: ", self.type)
    if t not in cbmtypes:
      ttyio.echo("invalid drive type")
      return
    ttyio.echo("selected %s" % (cbmtypes[t]))
    self.type = t

    self.image = bbsengine.inputfilename(self.args, "image name: ", self.image)

class StorageDeviceCMD(StorageDevice):
  def __init__(self, args, number, devicetype="CMD"):
    super().__init__(args, number) # , data:dict={}, **kwargs)
    self.hasrtc = True
    self.type = devicetype
    self.number = number
    self.image = None
    self.bin = None

  def edit(self, args):
    if self.hasrtc is True:
      if ttyio.inputboolean("use rtc? [Yn]: ", "Y") is True:
        self.usertc = True
        if ttyio.inputboolean("save rtc? [Yn]: ", "Y") is True:
          self.savertc = True
    self.image = bbsengine.inputfilename(self.args, "image filename: ", self.image)
    self.bin = bbsengine.inputfilename(self.args, "bin filename: ", self.bin)
    vicecommandline["-%d" % (self.number)] = self.image
    vicecommandline["-drive%dtype" % (self.number)] = self.type
#    vicecommandline["-9"] =  "cmddrive9.d4m"
#    vicecommandline["-drive9type"] = "4000"

  add = edit

  def __str__(self):
    buf = ""
    if self.usertc is True:
      buf += "rtc"
      if self.savertc is True:
        buf += " saved"
    return buf

class StorageDeviceREU(StorageDevice):
  def __init__(self, args):
    super().__init__(args) # , data:dict={}, **kwargs)

class StorageDevices(object):
  def __init__(self):
    self.devices = []
    self.subclasses = {
        "1001":    StorageDeviceCBM,
        "1540":    StorageDeviceCBM,
        "1541":    StorageDeviceCBM,
        "1542":    StorageDeviceCBM,
        "1570":    StorageDeviceCBM,
        "1571":    StorageDeviceCBM,
        "1581":    StorageDeviceCBM,
        "2031":    StorageDeviceCBM,
        "8050":    StorageDeviceCBM,
        "8250":    StorageDeviceCBM,
        "LTK":     StorageDeviceLTK,
        "2000":    StorageDeviceCMD,
        "4000":    StorageDeviceCMD,
        "4844":    StorageDeviceCMD
#        "RAMLINK": StorageDeviceRamlink
    }

  def append(self, storagedevice):
    if issubclass(type(storagedevice), StorageDevice) is True:
      self.devices.append(storagedevice)
      return

    ttyio.echo("StorageDevices.append() not passed a subclass of StorageDevice")
    return

  def __getitem__(self, index):
    return self.devices[index]

  def find(self, number):
#    ttyio.echo("StorageDevices.find.number=%r" % (number), level="debug")
    for d in self.devices:
      if d.number == number:
        return d
    return None

  def clear(self):
    self.devices = []

  def __len__(self):
    return len(self.devices)

  def summary(self, args, **kwargs):
    if len(storagedevices) == 0:
      ttyio.echo("no storage devices configured.")
      return True
    for sd in storagedevices:
      ttyio.echo(str(sd))

    return True

  def add(self, args, **kwargs):
#    ttyio.echo("entering storagedevices.add()")
    number = ttyio.inputinteger("{var:engine.menu.promptcolor}device number: {var:engine.menu.inputcolor}")
    ttyio.echo("{/all}")
    dt = drivetype(args, number)

    subclass = self.subclasses[dt]
    sd = subclass(args, number, dt)
    sd.add()
    ttyio.echo(str(sd), level="debug")
    if ttyio.inputboolean("add this device? [y{var:engine.currentoptioncolor}N{/all}]: ", "N") is True:
      storagedevices.append(sd) # [storagedevice.device] = storagedevice
    else:
      ttyio.echo("storage device not added.")

    return False

  def edit(self, args, **kwargs):
#    ttyio.echo("edit{/all}")
    if len(storagedevices) == 0:
      ttyio.echo("no storage devices defined.", level="error")
      return False
    number = ttyio.inputinteger("device number: ")
    d = self.find(number)
    if d is None:
      ttyio.echo("device #%d is not defined" % (number), level="error")
      return False
    d.edit()
    return True

  def kill(self, args, **kwargs):
    ttyio.echo("kill")
    if len(storagedevices) == 0:
      ttyio.echo("no storage devices defined.", level="error")
      return False
    device = ttyio.inputinteger(args, "kill which device?: ")
    if device is None or device == 0:
      ttyio.echo("no storage device number entered.")
      return False

    return False

storagedevices = StorageDevices()

def storage(args, **kwargs):
  global storagedevices

  bbsengine.setarea("vice: storage")

  done = False
  while not done:
    bbsengine.title("storage")
    ttyio.echo("[L]ist{f6}[A]dd{f6}[K]ill{f6}[E]dit{f6:2}[Q]uit{f6}")
    ch = ttyio.inputchar("{var:engine.menu.promptcolor}storage [LAKEQ]: {var:engine.menu.inputcolor}", "LAKEQ", "")
    if ch == "L":
      ttyio.echo("List{/all}")
      storagedevices.summary(args)
    elif ch == "A":
      ttyio.echo("Add{/all}")
      res = storagedevices.add(args)
    elif ch == "K":
      ttyio.echo("kill{/all}")
      res = storagedevices.kill(args)
    elif ch == "E":
      ttyio.echo("Edit{/all}")
      res = storagedevices.edit(args)
    elif ch == "Q":
      ttyio.echo("Quit{/all}")
      done = True
      break
  x = ""
  for sd in storagedevices:
    x += "%s " % (sd) # "% 2d: %s " % (sd.number, sd.type)
  bbsengine.poparea()
  return (True, x)

def oldstorage(args, **kwargs):
#  area("vice: storage")
#  title("vice: storage")

  useltk = setup["useltk"] if "useltk" in setup else True
  usecmd = setup["usecmd"] if "usecmd" in setup else False

  if useltk is True:
    ltk = ttyio.inputboolean("use ltk? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN")
  else:
    ltk = ttyio.inputboolean("use ltk? [y{bggray{white}N]: ", "N", "YN")
  if usecmd is True:
    cmd = ttyio.inputboolean("use cmd? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN")
  else:
    cmd = ttyio.inputboolean("use cmd? [y{bggray{white}N]: ", "N", "YN")

#  setup["useltk"] = ltk
#  setup["usecmd"] = cmd

  # handle hybrid!
  if ltk is True:
      ttyio.echo("Lt. Kernel")

#      setup["useltk"] = True
      ltkdevdefault = setup["ltkdev"] if "ltkdev" in setup else 8
      ltkdev = ttyio.inputinteger("ltk device number, 8..99: ", ltkdevdefault, verify=verifyLTKDevInRange)
      if ltkdev < 12 and ltkdev > 7:
        vicecommandline["-drive%dtype" % (ltkdev)] = "1581"

      setup["ltkdev"] = ltkdev
      vicecommandline["-cartcrt"] = bbsengine.inputfilename(args, "-cartcrt: ", os.path.join(args.basedir, "ltk.crt"), verify=bbsengine.verifyFileExistsReadable)
      vicecommandline["-ltkimage0"] = bbsengine.inputfilename(args, "-ltkimage0: ", os.path.join(args.basedir, "drive8-0.dlk"), verify=bbsengine.verifyFileExistsReadableWritable)
      vicecommandline["-ltkimage1"] = bbsengine.inputfilename(args, "-ltkimage1: ", os.path.join(args.basedir, "drive8-1.dlk"), verify=bbsengine.verifyFileExistsReadableWritable)
      vicecommandline["-ltkimage2"] = bbsengine.inputfilename(args, "-ltkimage2: ", os.path.join(args.basedir, "drive8-2.dlk"), verify=bbsengine.verifyFileExistsReadableWritable)
#      vicecommandline["-ltkimage3"] = inputfilename(args, "-ltkimage3: ", os.path.join(args.basedir, "drive8-3.dlk"), verify=verifyFileExistsReadableWritable)
#      vicecommandline["-ltkimage4"] = inputfilename(args, "-ltkimage4: ", os.path.join(args.basedir, "drive8-4.dlk"), verify=verifyFileExistsReadableWritable)
#      vicecommandline["-ltkimage5"] = inputfilename(args, "-ltkimage5: ", os.path.join(args.basedir, "drive8-5.dlk"), verify=verifyFileExistsReadableWritable)
#      vicecommandline["-ltkimage6"] = inputfilename(args, "-ltkimage6: ", os.path.join(args.basedir, "drive8-6.dlk"), verify=verifyFileExistsReadableWritable)
      vicecommandline["-ltkport"] = ttyio.inputinteger("Set LTK port number (0..15): ", 0, verify=verifyLTKPortInRange)

      # handle existing value
      ch = vicecommandline["-ltkio"] = ttyio.inputchar("Set LTK IO page (0: 0xDE00, {var:engine.currentoptioncolor}1: 0xDF00{/all}): ", "01", "1")
      if ch == "1":
        ttyio.echo("1: 0xDF00")
        ioaddrs["0xDF00"] = "ltkio"
        if "0xDE00" in ioaddrs and ioaddrs["0xDE00"] == "ltkio":
          del ioaddrs["0xDE00"]
      elif ch == "0":
        ttyio.echo("0: 0xDE00")
        ioaddrs["0xDE00"] = "ltkio"
        if "0xDF00" in ioaddrs and ioaddrs["0xDF00"] == "ltkio":
          del ioaddrs["0xDF00"]
      vicecommandline["-ltkio"] = ch

      ch = ttyio.inputboolean("use ltk dos72-s1 disk on device 9? [yN]: ", "N")
      if ch == "Y":
        vicecommandline["-9"] = os.path.join(args.basedir, "dos72-s1.d64")
        vicecommandline["-drive9type"] = "1541"
      elif ch == "N":
        ttyio.echo("No")
  if cmd is True:
#    setup["usecmd"] = True
    ttyio.echo("CMD")
    if "-ltkio" in vicecommandline and vicecommandline["-ltkio"] is not None and setup["ltkdev"] == 8:
      ttyio.echo("ltk assigned to drive %s" % (ltkdev))
      if ttyio.inputboolean("proceed? [yN]: ", "N", "YN") is True:
        vicecommandline["-8"] =  "dos-part1.dhd"
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
      if ttyio.inputboolean("Enable saving of RTC data to drive %d? [{var:engine.currentoptioncolor}Y{/all}n]: " % (drivenumber), "Y", "YN") is True:
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
      image = bbsengine.inputfilename(args, "drive %d image: " % (drivenumber), default, noneok=True, multiple=False)
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
  bbsengine.setarea("summary")
  bbsengine.title("summary")
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
  bbsengine.setarea("vice: default config")

  if ttyio.inputboolean("restore default config before processing options? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN") is True:
    vicecommandline["-default"] = None
  bbsengine.poparea()
  return True

def saveonviceexit(args):
  bbsengine.setarea("vice: save settings on exit")
  bbsengine.title("vice: save settings on vice exit")

  if ttyio.inputboolean("save vice settings on exit from vice? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y") is True:
    vicecommandline["-saveres"] = None
  else:
    vicecommandline["+saveres"] = None
  bbsengine.poparea()
  return True

def checkltkaciaconflict(args):
  bbsengine.setarea("vice: checkltkaciaconflict")
  bbsengine.title("vice: check for ltk / acia1 conflicts")

  ttyio.echo("check ltk and acia1 conflicts: ",end="")
  if "-aciabase" not in vicecommandline or "-ltkio" not in vicecommandlist:
    ttyio.echo("ltk or acia not defined.")
    return True

  if vicecommandline["-acia1base"] == vicecommandline["-ltkio"]:
      ttyio.echo("conflict.{f6}acia1base and ltkio are set to the same value (%s)" % (vicecommandline["-acia1base"]))
      return False
  return True

def savejson(args):
  bbsengine.setarea("savejson")
  bbsengine.title("save json file of setup data")
  
  if ttyio.inputboolean("save setup data? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y") is False:
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

  filename = bbsengine.inputfilename(args, "save json filename: ", default, noneok=True, multiple=False, verify=None)
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
  bbsengine.title("iocollision handling")
  if "-iocollision" in vicecommandline:
    default = ord("A") + int(vicecommandline["-iocollision"])
  else:
    default = "B"

  if default == "A":
    ttyio.echo("{var:engine.currentoptioncolor}[A] error message, detatch all involved carts{/all}")
  else:
    ttyio.echo("[A] error message, detatch all involved carts")

  if default == "B":
    ttyio.echo("{var:engine.currentoptioncolor}[B] error message, detach most recent involved cart{/all}")
  else:
    ttyio.echo("[B] error message, detach most recent involved cart")
  
  if default == "C":
    ttyio.echo("{var:engine.currentoptioncolor}[C] warning in log, bitwise-and valid return values{/all}")
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

def basedir(args):
  pass

def findioaddr(value):
  global ioaddrs

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

def main():
    parser = argparse.ArgumentParser("setupimagebbs")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", default=False, dest="debug")
    parser.add_argument("--basedir", action="store", dest="basedir", default="~jam/projects/gfd3/")
    args = parser.parse_args()
    # ttyio.echo("args=%r" % (args), level="debug")

    locale.setlocale(locale.LC_ALL, "")

    terminalwidth = ttyio.getterminalwidth()

    ttyio.echo("{f6:5}{curpos:%d,0}" % (ttyio.getterminalheight()-3))
    initscreen(bottommargin=1)

    bbsengine.setarea("setup image bbs")

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
    ttyio.setvariable("engine.currentoptioncolor", "{bggray}{white}")
    ttyio.setvariable("engine.areacolor", "{bggray}{white}")

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
#      { "name": "basedir",       "callback": basedir,     "label": "basedir"},
      { "name": "acia",          "callback": acia,        "label": "acia setup", "requires":()},
      { "name": "tcpser",        "callback": tcpser,      "label": "tcpser parameters", "requires":("acia",)},
      { "name": "rs232",         "callback": rs232,       "label": "rs232/ip232", "requires": ("tcpser", "acia",)},
      { "name": "drivesound",    "callback": drivesound,  "label": "drive sound"},
      { "name": "displaysync",   "callback": displaysync, "label": "display"},
      { "name": "storage",       "callback": storage,     "label": "storage"},
      { "name": "ramlink",       "callback": ramlink,     "label": "ramlink"},
      { "name": "sound",         "callback": sound,       "label": "sound"}
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
