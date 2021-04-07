import os
import re
import json
import locale
import socket
import argparse
import readline
import subprocess
import ttyio4 as ttyio

# set model to ntsc (64C)
# pfiles lu0, everything else on lu1, except for mail on lu2
# always set acia to $DExx. ltk defaults to $DFxx
# CMDFD4000 is compat w d64, d81, etc. the glitch is you need to load the dir so the disk is "recognized"
#
# from 2021-03-28 meeting w larry and al:
# x64sc -default +acia1 -ntsc -rsuser -rsdev1 localhost:25232 -rsdev1ip232 -rsdev1baud 2400 -rsdev2 rsdev2 +rsdev2ip232 -rsdev3 rsdev3 +rsdev3ip232 -rsdev4 rsdev4 +rsdev4ip232 +rsuser -dos4000 sandbox/cmd-fd-4000-dos-v1.40-fd-350022.bin -drive9type 4000 -8 dos-part1.dhd -9 cmddrive9.d4m -10 cmddrive10.d4m -11 cmddrive11.d4m
# tcpser -I -s 2400 -v 25232 -p 6400 -i e0v0s0=1s2=27 -t sI -l 7
vicecommandline = {}
tcpsercommandline = {}
localhost = "localhost"
ioaddrs = []

def initscreen(topmargin=0, bottommargin=0):
  terminalheight = ttyio.getterminalheight()
  # ttyio.echo("initscreen.100: terminalheight=%r" % (terminalheight))
  ttyio.echo("{decsc}{decstbm:%d,%d}{decrc}" % (topmargin, terminalheight-bottommargin))

def updatetopbar(args, area:str):
  if args.debug is True:
    return

  terminalwidth = ttyio.getterminalwidth()
  # ttyio.echo("{decsc}{home}%s{decrc}" % (buf.ljust(terminalwidth)), end="")
  buf = area.ljust(terminalwidth-2, " ")
  ttyio.echo("{decsc}{/all}{home}{bggray}{white} %s{el}{decrc}" % (buf), wordwrap=False)
  return

# @since 20210222
def updatebottombar(buf:str):
  terminalheight = ttyio.getterminalheight()
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

  updatebottombar("{bggray}{white}%s{/all}" % (buf.ljust(width-2, " ")))
  return

def checklocalhostdns(args):
  ttyio.echo("checklocalhostdns.100: checking...", level="debug")
  try:
    res = socket.gethostbyname("localhost")
  except:
    ttyio.echo("{bgred}{orange}dns check for 'localhost' failed, reverting to ipv4 address.{/all}")
    return "127.0.0.1"
  else:
    ttyio.echo("{bglightgreen}{black}dns check for 'localhost' passed.{/all}")
    return "localhost"

def verifyFileExistsReadable(args, filename):
  filename = os.path.expanduser(filename)
  filename = os.path.expandvars(filename)
  ttyio.echo("args=%r filename=%r" % (args, filename))

  if args.debug is True:
    ttyio.echo("filename=%r" % (filename), level="debug")

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
  if ttyio.inputboolean("use settings for 'gfd3'? [Yn]: ", "Y", "YN") is True:
    vicecommandline["-10"] = "/home/jam/projects/gfd3/drive10.d81"
    vicecommandline["-11"] = "/home/jam/projects/gfd3/drive11.d81"
    vicecommandline["-drive10type"] = "1581"
    vicecommandline["-drive11type"] = "1581"
    vicecommandline["-ltkimage0"] = "/home/jam/projects/gfd3/drive8-0.dlk"
    vicecommandline["-ltkimage1"] = "/home/jam/projects/gfd3/drive8-1.dlk"
    vicecommandline["-ltkimage2"] = "/home/jam/projects/gfd3/drive8-2.dlk"
  return None

def keyboard(args):
  keyboards = ("0: Symbpolic", "1: Positional", "2: symbolic (user)", "3: positional (user)")
  ch = ttyio.inputchar("Specify index of keymap file ({bggray}{white}0:symbolic{/all}, 1:positional, 2:symbolic (user), 3:positional (user))? [0123]: ","0123", "0")
  if ch == "0":
    ttyio.echo("0:symbolic")
  elif ch == "1":
    ttyio.echo("1:positional")
  elif ch == "2":
    ttyio.echo("2:symbolic (user)")
  elif ch == "3":
    ttyio.echo("3:positional (user)")

  vicecommandline["-keymap"] = ch
  return

def cmd4000(args):
  if ttyio.inputboolean("enable cmd fd-4000 on device 9? [Yn]: ", "Y", "YN") is True:
    vicecommandline["-dos4000"] = inputfilename(args, "dos4000 filename: ", "cmd-fd-4000-dos-v1.40-fd-350022.bin")
    vicecommandline["-drive9type"] = "4000"
    if ttyio.inputboolean("enable drive 9 rtc save? [Yn]: ", "Y", "YN") is True:
      vicecommandline["-drive9rtcsave"] = None
    else:
      vicecommandline["+drive9rtcsave"] = None

def ds12c887rtc(args):
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
    return
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

  defaultvalue = ""

  menu = []
  ch = ord("A")
  options = ""
  for c in addresschoices:
    i = ch - ord("A")
    if currentaddr == addresschoices[i]:
      menu.append("{bggray}{white}[%s] %s{/all}" % (chr(ch), addresschoices[i]))
      defaultvalue = chr(ch)
    else:
      menu.append("[%s] %s" % (chr(ch), addresschoices[i]))
    options += chr(ch)
    ch += 1

  ch = ttyio.inputchar("Address "+" ".join(menu)+": ", options, defaultvalue, noneok=False)
  addr = addresschoices[ord(ch) - ord("A")]
  ioaddrs.append(addr)
  vicecommandline["-ds12c887rtcbase"] = addr
  ttyio.echo(addr)

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

#  if "-ds12c887rtsrunning" in vicecommandline:
#    ch = ttyio.inputchar("Set the RTC oscillator to {bggray}{white}[R]unning{/all} or [H]alted", "RH", "R")
#  elif "-ds12c887rtchalted" in vicecommandline:
#    ch = ttyio.inputboolean("Set the RTC oscillator to [R]unning or {bggray}{white}[H]alted", "RH", "H")
#  else:
#    ch = ttyio.inputchar("Set the RTC oscillator to {bggray}{white}[R]unning{/all} or [H]alted", "RH", "R")

  if ch is False:
    vicecommandline["-ds12c887running"] = None
    if "-ds12c887halted" in vicecommandline:
      del vicecommandline["-ds12c887halted"]
  else:
    vicecommandline["-ds12c887halted"] = None
    if "-ds12c887running" in vicecommandline:
      del vicecommandline["-ds12c887running"]

  ttyio.echo()
  # remove contents of -ltkio from choices so there is not a conflict.
  return

def rs232(args):
  area("vice")
  title("vice: rs232")
  vicecommandline["+rsuser"] = None
  vicecommandline["-rsdev4"] = "%s:%s" % (localhost, tcpsercommandline["-v"])
  vicecommandline["-rsdev4ip232"] = None
  vicecommandline["-rsdev4baud"] = tcpsercommandline["-s"] # 38400

  ttyio.echo("configured rsdev4 as ip232.")
  return

def acia(args):
  area("vice")
  title("vice: acia")

  if ttyio.inputboolean("Enable the ACIA RS232 interface emulation (Swiftlink)? [Yn]: ", "Y", "YN") is False:
    vicecommandline["+acia1"] = None
    return

  ch = ttyio.inputchar("Set the ACIA mode (0: Normal, {bggray}{white}[1]: Swiftlink{/all}, 2: Turbo232): ", "012", "1")
  if ch == "0":
    ttyio.echo("0: Normal")
  elif ch == "1":
    ttyio.echo("1: Swiftlink")
  elif ch == "2":
    ttyio.echo("2: Turbo32")

  vicecommandline["-acia1mode"] = ch

  ch = ttyio.inputchar("Base address of the ACIA cartridge ({bggray}0: 0xDE00{/all}, 1: 0xDF00): ", "01", "0")
  if ch == "0":
    ttyio.echo("0: 0xDE00")
    vicecommandline["-acia1base"] = "0xDE00"
    ioaddrs.append("0xDE00")
  else:
    ttyio.echo("1: 0xDF00")
    vicecommandline["-acia1base"] = "0xDF00"
    ioaddrs.append("0xDF00")

  ch = ttyio.inputchar("Set the ACIA interrupt (0: None, {bggray}{white}[1]: NMI{/all}, 2: IRQ): ", "012", "1")
  if ch == "0":
    ttyio.echo("0: None")
  elif ch == "1":
    ttyio.echo("1: NMI")
  elif ch == "2":
    ttyio.echo("2: IRQ")
  vicecommandline["-acia1irq"] = ch

  vicecommandline["-myaciadev"] = 3
  vicecommandline["-acia1"] = None
  return

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
  if args.debug is True:
    ttyio.echo("tcpser.100: acia1mode=%r" % (acia1mode), level="debug")
  if acia1mode == "1":
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

def ramlink(args):
  area("vice")
  title("vice: ramlink")

  if args.ramlink is True:
    ttyio.echo("ramlink enabled by command line option")
  else:
    if ttyio.inputboolean("use ramlink? ", "N", "YN") is False:
          vicecommandline["-ramlink"] = None
          return

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

  return

def displaysync(args):
  area("vice")
  title("vice: display sync")
  sync = ttyio.inputchar("{bggray}{white}[N]TSC{/all} or [P]AL? ", "NP", "N")
  if sync == "N":
    ttyio.echo("NTSC")
    vicecommandline["-ntsc"] = None
  elif sync == "P":
    ttyio.echo("PAL")
    vicecommandline["-pal"] = None
  return

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

def storage(args):
  area("vice")
  title("vice: storage")
  storage = args.storage.upper() if args.storage is not None else None
  if args.debug is True:
    ttyio.echo("storage.100: args=%r, storage=%r" % (args, storage))
  if storage is not None:
    if storage == "LTK":
      s = "L"
    elif storage == "CMD":
      s = "C"
  else:
    s = ttyio.inputchar("{bggray}{white}[L]t Kernel{/all}, [C]MD, or [N]either? ", "LCN", "L")

  # x64sc.exe -cartcrt ltk.crt -ltkimage0 disk0.dlk -ltkimage1 disk1.dlk
  # -ltkimage2 disk2.dlk -drive8type 1541 -drive9type 0 -8 dos72-s1.d64
  # -kernal kernal

  if s == "L":
      ttyio.echo("Lt. Kernel")
      args.storage = "LTK"
      vicecommandline["-cartcrt"] = inputfilename(args, "-cartcrt: ", "ltk.crt")
      vicecommandline["-ltkimage0"] = inputfilename(args, "-ltkimage0: ", "drive8-0.dlk")
      vicecommandline["-ltkimage1"] = inputfilename(args, "-ltkimage1: ", "drive8-1.dlk")
      vicecommandline["-ltkimage2"] = inputfilename(args, "-ltkimage2: ", "drive8-2.dlk")
      vicecommandline["-ltkport"] = ttyio.inputstring("Set LTK port number (0..15): ", "0", verify=verifyLTKPortInRange)

      ch = vicecommandline["-ltkio"] = ttyio.inputchar("Set LTK IO page (0: $DExx, {bggray}{white}1: $DFxx{/all}): ", "01", "1")
      if ch == "1":
        ttyio.echo("1: $DFxx (default)")
      elif ch == "0":
        ttyio.echo("0: $DExx")
      vicecommandline["-ltkio"] = ch

      ch = ttyio.inputboolean("use ltk dos72-s1 disk on device 9? [yN]: ", "N", "YN")
      if ch == "Y":
        vicecommandline["-9"] = "dos72-s1.d64"
        vicecommandline["-drive9type"] = "1541"
      elif ch == "N":
        ttyio.echo("No")
  elif s == "C":
      args.storage = "CMD"
      ttyio.echo("CMD")
      vicecommandline["-8"] =  "dos-part1.dhd" # what device type?

      vicecommandline["-9"] =  "cmddrive9.d4m"
      vicecommandline["-drive9type"] = "4000"

      vicecommandline["-10"] = "cmddrive10.d4m"
      vicecommandline["-drive10type"] = "4000"

      vicecommandline["-11"] = "cmddrive11.d4m"
      vicecommandline["-drive11type"] = "4000"
  elif s == "N":
      ttyio.echo("Neither")

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

    if dt == "4000" or dt == "2000":
      if ttyio.inputboolean("Enable saving of RTC data to drive %d? [Yn]: " % (drivenumber), "Y", "YN") is True:
        vicecommandline["-drive%drtcsave" % (drivenumber)] = None
      else:
        vicecommandline["+drive%drtcsave" % (drivenumber)] = None

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

def summary(args):
  area("setupimagebbs")
  title("summary")
  if "-default" in vicecommandline:
    resetdefaults = True
    del vicecommandline["-default"]
  else:
    resetdefaults = False

  opts = []

  if resetdefaults is True:
    ttyio.echo("using -default")
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

def verifyREUSize(args, buf):
  if buf in ["128", "256", "512", "1024", "2048", "4096", "8192", "16384"]:
    return True
  return False

class completeREUSize(object):
  def __init__(self, args, vocab):
      # ttyio.echo("completeAttributeName.100: called")
      self.vocab = vocab

  def complete(self:object, text:str, state:int):
    results = [x for x in self.vocab if x.startswith(text)] + [None]
    return results[state]

def reu(args):
  area("vice: RAM Expansion Unit")
  title("vice: RAM Expansion Unit")

  if ttyio.inputboolean("Enable the RAM Expansion Unit? [yN]: ", "N", "YN") is True:
    vicecommandline["-reu"] = None
    ttyio.inputinteger("Size of the RAM expansion unit. (128/256/512/1024/2048/4096/8192/16384): ", 512, verify=verifyREUSize)
    vicecommandline["-reuimage"] = inputfilename(args, "REU image: ")
    if ttyio.inputboolean("Allow writing to REU image? [Yn]: ", "Y", "YN") is True:
      vicecommandline["-reuimagerw"] = None
    else:
      vicecommandline["+reuimagerw"] = None
    vicecommandline["-cartreu"] = inputfilename(args, "Attach raw REU cartridge image: ")
  else:
    vicecommandline["+reu"] = None
  return

def defaultconfig(args):
  area("vice")

  if ttyio.inputboolean("restore default config before processing options? [Yn]: ", "Y", "YN") is True:
    vicecommandline["-default"] = None

def saveonviceexit(args):
  area("vice")
  title("vice: save settings on vice exit")

  if ttyio.inputboolean("save vice settings on exit from vice? [Yn]: ", "Y", "YN") is True:
    vicecommandline["-saveres"] = None
  else:
    vicecommandline["+saveres"] = None

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
    return

  data = {}

  data["vice"] = {}
  for k, v in vicecommandline.items():
    data["vice"][k] = v

  data["tcpser"] = {}
  for k, v in tcpsercommandline.items():
    data["tcpser"][k] = v

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

def drivesound(args):
  if ttyio.inputboolean("Enable sound emulation of disk drives [Yn]: ", "Y", "YN") is True:
    vicecommandline["-drivesound"] = None
    vol = ttyio.inputinteger("Set volume for disk drive sound emulation (0-4000): ", 100)
    vicecommandline["-drivesoundvolume"] = vol
  else:
    vicecommandline["+drivesound"] = None

def iocollision(args):
  ch = ttyio.inputchar("Select the way the I/O collisions should be handled ([0]: error message and detach all involved carts, [1]: error message and detach last attached involved carts, [2]: warning in log and 'AND' the valid return values", "012", "0")
  vicecommandline["-iocollision"] = ch
  return

def main():
    # parser = OptionParser(usage="usage: %prog [options] projectid")
    parser = argparse.ArgumentParser("setupimagebbs")
    
    # parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    
    # parser.add_option("--debug", default=False, action="store_true", help="run %prog in debug mode")
    parser.add_argument("--debug", action="store_true", default=False, dest="debug")

    parser.add_argument("--storage", action="store", choices=["ltk", "cmd"], dest="storage")
    # parser.add_argument("--ramlink", action="store_true", dest="ramlink")
    parser.add_argument("--basedir", action="store", dest="basedir", default="sandbox/")
    args = parser.parse_args()
    # ttyio.echo("args=%r" % (args), level="debug")

    locale.setlocale(locale.LC_ALL, "")

    terminalwidth = ttyio.getterminalwidth()

    if args.debug is True:
        ttyio.echo("setupbbs.main.100: args=%r" % (args))

    ttyio.echo("{clear}{home}")
    initscreen(bottommargin=1)

    if args.basedir and args.debug is True:
      ttyio.echo("setupbbs.main.120: basedir=%r" % (args.basedir))
    args.basedir = os.path.expanduser(args.basedir)
    args.basedir = os.path.expandvars(args.basedir)
    args.basedir = ttyio.inputstring("basedir: ", args.basedir, args=args)

    localhost = checklocalhostdns(args)

    ds12c887rtc(args)
    ds12c887rtc(args)
    return

    tests = (
      # "loadjson",
      "checktcpser",
      "checkvice",
      "gfd3",
      "defaultconfig",
      "sounddrive",
      "acia",
      "tcpser",
      "displaysync",
      "rs232",
      "cmd4000",
      "storage",
      "iocollision",
      "checkltkaciaconflict",
      "keyboard",
      "saveonviceexit",
      #"ramlink",
      #"reu",
      "summary",
      "savejson"
    )

    for t in tests:
      if args.debug is True:
        ttyio.echo("t=%r" % (t), level="debug")
      func = eval(t)
      if callable(func) is False:
        ttyio.echo("%r is not callable." % (t), level="error")
        continue
      res = func(args)
      if res is False:
        if ttyio.inputboolean("{bgred}{white}%r failed.{/all}{f6}proceed anyway? [Yn]: " % (t), "Y", "YN") is False:
          ttyio.echo("{bgred}{white}aborted{/all}", end="")
          return False
      ttyio.echo()

    return    

if __name__ == "__main__":
  try:
    main()
  finally:
    updatebottombar("")
    ttyio.echo("{reset}{/all}")
