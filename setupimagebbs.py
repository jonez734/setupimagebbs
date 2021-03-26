import os
import re
import locale
import argparse
import readline
import subprocess

import ttyio4 as ttyio
import bbsengine5 as bbsengine

vicecommandline = {}

def checktcpser(args, filename="tcpser"): # filename="/home/jam/tmp/tcpser-1.1.4/tcpser"):
  res = subprocess.run([filename, "-V"], capture_output=True, text=True)

  # look for "invalid option -- 'V'" -- (-V added in 1.1.4, older versions will complain of invalid option)
  # ttyio.echo("%r" % (res.stderr))
  # ttyio.echo("stdout=%r" % (res.stdout))
  if res.stdout.find("invalid option -- 'V'") > -1 or res.stderr.find("invalid option -- 'V'") > -1:
    ttyio.echo("The version of tcpser installed is not compatible with imagebbs (>=1.1.4k).")
    return False

  if res.stdout.find("(TCPSER) 1.1.4") > -1 or res.stderr.find("(TCPSER) 1.1.4") > -1:
    ttyio.echo("This version of tcpser should be compatible with imagebbs")
    return True

def checkvice(args, filename="x64sc"):
  res = subprocess.run([filename, "--features"], capture_output=True, text=True)

  for match in re.finditer(r"^(\S+)\s+(yes|no)\s+(.*)", res.stdout, re.MULTILINE):
    define = match.group(1)
    value = True if match.group(2) ==  "yes" else False
    description = match.group(3)
    if define == "HAVE_RS232NET":
      ttyio.echo("{bold}%s: %s (%s){/bold}" % (description, value, define))
      if value is False:
        ttyio.echo("HAVE_RS232NET is not enabled.")
        return False
      else:
        ttyio.echo("HAVE_RS232NET is enabled.")
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

def verifyFileExistsReadable(args, filename):
  filename = os.path.expanduser(filename)
  filename = os.path.expandvars(filename)
  ttyio.echo("filename=%r" % (filename))
  if os.access(filename, os.R_OK) is True and os.path.isfile(filename) is True:
    return True
  return False

# @see https://www.digitalocean.com/community/tutorials/how-to-use-subprocess-to-run-external-programs-in-python-3
def verifyC64Cart(args, filename):
  f = os.path.join(args.basedir, filename)
  f = os.path.expanduser(f)
  f = os.path.expandvars(f)
  res = subprocess.run(["file", "--brief", f], capture_output=True, text=True)
  ttyio.echo("res.stdout=%r" % (res.stdout))
  return

def verifyLTKPortInRange(args, port):
  try:
    port = int(port)
  except:
    return False
  if port < 0 or port > 15:
    return False
  return True

def title(buf):
  return bbsengine.title(buf, hrcolor="{white}", titlecolor="{bggray}{white}")

def inputfilename(args, prompt, default, verify=verifyFileExistsReadable, **kw):
  if args.basedir is not None and default is not None:
    default = os.path.join(args.basedir, default)
  ttyio.echo("inputfilename.100: delims=%r" % (readline.get_completer_delims()))
  return ttyio.inputstring(prompt, default, verify=verify, completerdelims="\t\n", **kw)

def updatetopbar(args, area):
    terminalwidth = ttyio.getterminalwidth()
    bbsengine.updatetopbar("{bggray}{white}%s" % (area.ljust(terminalwidth-2)))
    return

def phonebook(args):
  book = []
  book.append({"shortname":"ci1", "host": "cib.dyndns.org:6400", "sysop": "x-tec", "system": "Image 1.2"})
  book.append({"shortname": "ci2", "host": "cib.dyndns.org:6401", "sysop": "x-tec", "system": "Image 1.2"})
  
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

tcpsercommandline = {}

def tcpser(args):
  title("tcpser")

  tcpsercommandline["-s"] = ttyio.inputinteger("speed in bits per second (-s): ", 2400)
  tcpsercommandline["-v"] = ttyio.inputinteger("tcp port for VICE RS232 (-v): ", 25232)
  tcpsercommandline["-p"] = ttyio.inputstring("port or address:port (-p): ", "6400")

  tcpsercommandline["-i"] = ttyio.inputstring("modem init string (-i): at", "e0v0s0=1s2=27")

  traceflags = ""
  title("trace flags")
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
  ttyio.echo("buf=%r" % (buf))
  level = None
  for i in range(0, len(vocab)):
    if vocab[i] == buf:
      level = i
      break

  if args.debug is True:
    ttyio.echo("level=%r" % (i))
  tcpsercommandline["-l"] = i

#define LOG_TRACE 10
#define LOG_ALL 7
#define LOG_ENTER_EXIT 6
#define LOG_DEBUG 5
#define LOG_INFO 4
#define LOG_WARN 3
#define LOG_ERROR 2
#define LOG_FATAL 1
#define LOG_NONE 0

def ramlink(args):
  title("ramlink")

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

def drivetype(args, devicenumber, oldvalue=None):
    types = {
        "1540": "CBM 1540",
        "1541": "CBM 1541",
        "1541-II": "CBM 1541-II",
        "1570": "CBM 1570",
        "1571": "CBM 1571",
        "1581": "CBM 1581"
    }

    if args.storage == "CMD":
        types["FD-2000"] = "CMD FD-2000"
        types["FD-4000"] = "CMD FD-4000"

    if args.debug is True:
      ttyio.echo("drivetype.100: oldvalue=%r" % (oldvalue))

    default = "N"
    options = "N"
    menu = {}
    char = ord("A")
    title("device %d setup" % (devicenumber))
    # updatetopbar(args, "storage")
    for k, v in types.items():
      if k == oldvalue:
        ttyio.echo("{bggray}{white}[%s] %s{/all}" % (chr(char), v))
        default = chr(char)
      else:
        ttyio.echo("[%s] %s" % (chr(char), v))

      options += chr(char)

      menu[chr(char)] = k

      char += 1

    ttyio.echo("[N] None")

    dt = ttyio.inputchar("device %d type: " % (devicenumber), options, default)
    # ttyio.echo("menu=%r" % (menu), interpret=False)
    if dt in menu:
        ttyio.echo("%s" % (menu[dt]))
        return menu[dt]
    ttyio.echo("None")
    return None

def storage(args):
  title("storage")

  if args.debug is True:
    ttyio.echo("storage.100: storage=%r" % (args.storage))
  if args.storage is not None:
    if args.storage.upper() == "LTK":
      s = "L"
    elif args.storage.upper() == "CMD":
      s = "C"
  else:
    s = ttyio.inputchar("[L]t Kernel or [C]MD? ", "LC", "")

  # x64sc.exe -cartcrt ltk.crt -ltkimage0 disk0.dlk -ltkimage1 disk1.dlk
  # -ltkimage2 disk2.dlk -drive8type 1541 -drive9type 0 -8 dos72-s1.d64
  # -kernal kernal

  if s == "L":
      ttyio.echo("Lt. Kernel")
      args.storage = "LTK"
      vicecommandline["-cartcrt"] = inputfilename(args, "-cartcrt: ", "ltk.crt")
      vicecommandline["-ltkimage0"] = inputfilename(args, "ltkimage0: ", "disk0.dlk")
      vicecommandline["-ltkimage1"] = inputfilename(args, "ltkimage1: ", "disk1.dlk")
      vicecommandline["-ltkimage2"] = inputfilename(args, "ltkimage2: ", "disk2.dlk")
      vicecommandline["-ltkport"] = ttyio.inputstring("Set LTK port number (0..15): ", "0", verify=verifyLTKPortInRange)

      ch = vicecommandline["-ltkio"] = ttyio.inputchar("Set LTK IO page (0=$DExx, 1=$DFxx=default): ", "01", "1")
      if ch == "1":
        ttyio.echo("$DFxx (default)")
      elif ch == "0":
        ttyio.echo("$DExx")
      vicecommandline["-ltkio"] = ch

      ch = ttyio.inputboolean("use ltk dos72-s1 disk on device 8? ", "N", "YN")
      if ch == "Y":
        vicecommandline["-8"] = "dos72-s1.d64"
        vicecommandline["-drive8type"] = "1541"
      elif ch == "N":
        ttyio.echo("No")
  elif s == "C":
      args.storage = "CMD"
      ttyio.echo("CMD")
      vicecommandline["-8"] =  "dos-part1.dhd" # what device type?
      vicecommandline["-9"] =  "cmddrive9.d4m"
      vicecommandline["-10"] = "cmddrive10.d4m"
      vicecommandline["-11"] = "cmddrive11.d4m"

  for drivenumber in range(8,11):
    default = None
    option = "-drive%dtype" % (drivenumber)
    #ttyio.echo("main.100: option=%r" % (option))
    #ttyio.echo("main.120: vicecommandline=%r" % (vicecommandline), interpret=False)
    if option in vicecommandline:
      default = vicecommandline[option]
    dt = drivetype(args, drivenumber, default)
    if dt is not None:
      vicecommandline[option] = dt
    else:
      continue

    default = None
    option = "-%d" % (drivenumber)
    if option in vicecommandline:
      default = vicecommandline[option]
    image = inputfilename(args, "drive %d image: " % (drivenumber), default)
    vicecommand[option] = image

def summary(args):
    title("summary")

    opts = []
    for k, v in vicecommandline.items():
      if v is not None:
        buf = "%s %s" % (k, v)
      else:
        buf = "%s" % (k)

      opts.append(buf)
    ttyio.echo("x64sc %s" % (" ".join(opts)))

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
  if buf == "128" or buf == "256" or buf == "512" or buf == "1024" or buf == "2048" or buf == "4096" or buf == "8192" or buf == "16384":
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
  title("RAM Expansion Unit")

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

def main():
    # parser = OptionParser(usage="usage: %prog [options] projectid")
    parser = argparse.ArgumentParser("setupimagebbs")
    
    # parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    
    # parser.add_option("--debug", default=False, action="store_true", help="run %prog in debug mode")
    parser.add_argument("--debug", action="store_true", dest="debug")

    # @see https://stackoverflow.com/questions/44342813/multiple-choices-command-line-argument
    # @see https://stackoverflow.com/questions/56119177/how-to-make-a-python-script-tab-complete-directories-in-terminal
    # @see https://stackoverflow.com/questions/16068607/how-to-suggest-files-with-tab-completion-using-readline
    # @see https://stackoverflow.com/questions/10487827/why-am-i-forced-to-os-path-expanduser-in-python
    # @see https://docs.python.org/3/library/os.path.html
    # @see https://stackoverflow.com/questions/33038056/deactivate-readline-autocompletion
    parser.add_argument("--storage", action="store", choices=["ltk", "cmd"], dest="storage")
    parser.add_argument("--ramlink", action="store_true", dest="ramlink")
    parser.add_argument("--basedir", action="store", dest="basedir", default=".")
    args = parser.parse_args()
    # ttyio.echo("args=%r" % (args), level="debug")

    locale.setlocale(locale.LC_ALL, "")

    terminalwidth = ttyio.getterminalwidth()

    if args.debug is True:
        ttyio.echo("setupbbs.main.100: args=%r" % (args))

    if args.basedir and args.debug is True:
      ttyio.echo("setupbbs.main.120: basedir=%r" % (args.basedir))

    if checktcpser(args) is False:
      ttyio.echo("blah")
      if ttyio.inputboolean("checktcpser failed. proceed? ", "", "YN") is False:
        return
    else:
      ttyio.echo("tcpser: yes!")

    if checkvice(args) is False:
      ttyio.echo("foo")
      if ttyio.inputboolean("checkvice failed. proceed? ", "", "YN") is False:
        return
    else:
      ttyio.echo("vice: yes!")

    storage(args)
    #ramlink(args)
    #reu(args)
    tcpser(args)
    summary(args)

    return    

if __name__ == "__main__":
    main()
    ttyio.echo("{reset}{/all}")
