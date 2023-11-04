import ttyio6 as ttyio
import bbsengine6 as bbsengine

def init(args, **kw):
    return True
    
def buildargs(args, **kw):
    return None

def access(args, op, **kw):
    return True

def sync(args, **kw):
  vice = kw["vice"] if "vice" in kw else {}
  soundstatus = kw["soundstatus"] if "soundstatus" in kw else []

  menuitem = kw["menuitem"] if "menuitem" in kw else None

  status = []
  sync = vice["-soundsync"] if "-soundsync" in vice else "0"
  prompt = "sync "
  if sync == "0":
    prompt += "{var:currentoptioncolor}0: system{/all} "
  else:
    prompt += "0: system "
  if sync == "1":
    prompt += "{var:currentoptioncolor}1: mono{/all} "
  else:
    prompt += "1: mono "
  if sync == "2":
    prompt += "{var:currentoptioncolor}2: stereo{/all}"
  else:
    prompt += "2: stereo"
  prompt += ": "
  ch = ttyio.inputchar(prompt, "012", sync)
  vice["-soundsync"] = ch
  if ch == "0":
    ttyio.echo("system")
    status.append("sync: system")
  elif ch == "1":
    ttyio.echo("mono")
    status.append("sync: mono")
  elif ch == "2":
    ttyio.echo("stereo")
    status.append("sync: stereo")
  soundstatus.append(" ".join(status))
  return (True, status)

def device(args, **kw):
  vice = kw["vice"] if "vice" in kw else {}
  device = vice["-sounddev"] if "-sounddev" in vice else "pulse"
  status = []
  soundstatus = kw["soundstatus"] if "soundstatus" in kw else []

  ttyio.echo(f"sound.100: {device=}", level="debug")

  opts = []
  if device == "pulse":
    opts.append("{var:currentoptioncolor}[P]ulse{/all}")
    currentoption = "P"
  else:
    opts.append("[P]ulse")
  if device == "alsa":
    opts.append("{var:currentoptioncolor}[A]LSA{/all}")
    currentoption = "A"
  else:
    opts.append("[A]LSA")
  if device == "sdl":
    opts.append("{var:currentoptioncolor}[S]DL{/all}")
    currentoption = "S"
  else:
    opts.append("[S]DL")
  if device == "dummy":
    opts.append("{var:currentoptioncolor}[D]ummy{/all}")
    currentoption = "D"
  else:
    opts.append("[D]ummy")
  dev = ttyio.inputchar("%s: " % (" ".join(opts)), "PASD", currentoption)
  if dev == "P":
    ttyio.echo("Pulse")
    vice["-sounddev"] = "pulse"
    status.append("dev: pulse")
  elif dev == "A":
    ttyio.echo("ALSA")
    vice["-sounddev"] = "alsa"
    status.append("dev: alsa")
  elif dev == "S":
    ttyio.echo("SDL")
    vice["-sounddev"] = "sdl"
    status.append("dev: sdl")
  elif dev == "D":
    ttyio.echo("Dummy")
    vice["-sounddev"] = "dummy"
    status.append("dev: dummy")
  soundstatus.append(" ".join(status))
  return (True, status)

def volume(args, **kw):
  soundstatus = kw["soundstatus"] if "soundstatus" in kw else []
  vice = kw["vice"] if "vice" in kw else {}

  volume = vice["-soundvolume"] if "-soundvolume" in vice else "70"
  vol = ttyio.inputinteger("{var:promptcolor}soundvolume {var:optioncolor}(0-100){var:promptcolor}: {var:inputcolor}", volume)
  if vol > 100 or vol < 1:
    ttyio.echo("volume out of range", level="error")
    return False

  vice["-soundvolume"] = vol
  soundstatus.append(f"{vol=}")
  return True

def drivesound(args, **kw):
  vice = kw["vice"] if "vice" in kw else {}
  menuitem = kw["menuitem"] if "menuitem" in kw else None

  status = []
  if ttyio.inputboolean("{var:promptcolor}Enable sound emulation of disk drives? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y") is True:
    volume = ttyio.inputinteger("{var:promptcolor}drive sound volume? {var:optioncolor}[0-100]{var:promptcolor}: {var:inputcolor}", 70)
    if "+drivesound" in vice:
      del vice["+drivesound"]
    vice["-drivesound"] = None
    vice["-drivesoundvolume"] = volume
  else:
    if "-drivesound" in vice:
      del vice["-drivesound"]
    if "-drivesoundvolume" in vice:
      del vice["-drivesoundvolume"]
    vice["+drivesound"] = None
    status.append("(disabled)")
  if "-drivesound" in vice:
    status.append(f"vol={vice['-drivesoundvolume']}")# % (vice["-drivesoundvolume"]))

#  soundstatus.append("drivesound: vol=%s" % (vice["-drivesoundvolume"]))
  menuitem.status = True
  menuitem.description = f"{vice['-drivesoundvolume']=}"
  return (True, status)

def main(args, **kw):
  ttyio.echo("sound")

  vice = kw["vice"] if "vice" in kw else {}

  soundstatus = []
  menuitem = kw["menuitem"] if "menuitem" in kw else None

  bbsengine.util.heading("sound")

  if ttyio.inputboolean("{var:promptcolor}enable sound? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y", "YN") is False:
    vice["+sound"] = None
    if "-sound" in vice:
      del vice["-sound"]
    menuitem.result = True
    menuitem.description = "(disabled)"
    return True

  if "+sound" in vice:
    del vice["+sound"]
  vice["-sound"] = None

  menuitems = [
    bbsengine.menu.Item("A", "sync", sync),
    bbsengine.menu.Item("B", "volume", volume),
    bbsengine.menu.Item("C", "device", device),
    bbsengine.menu.Item("D", "drive sound", drivesound),
  ]
#  menuitems = [
#    { "name": "soundsync",   "module": "soundsync",     "label": "sync"},
#    { "name": "soundvolume", "module": "soundvolume",   "label": "volume"},
#    { "name": "sounddev",    "module": "sounddev",      "label": "device"},
#    { "name": "drivesound",  "module": "drivesound",    "label": "drive sound"},
#  ]
  menu = bbsengine.menu.Menu(args, "sound", menuitems, **kw)
  done = False
  while not done:
    op = menu.run("sound: ")
    if op.menuitem.key == "X":
      ttyio.echo("exit")
      break

#    op.menuitem.description = " ".join(soundstatus)
    kw["menuitem"] = op.menuitem
    res = bbsengine.module.runcallback(args, op.menuitem.module, soundstatus=soundstatus, **kw)
#    ttyio.echo(f"modem.100: {kw=}", level="debug")
#    res = module.runsubmodule(args, res.menuitem.module, **kw) # setup=setup, vice=vice, **kw)
#    ttyio.echo(f"modem.120: {kw=}", level="debug")
  menuitem.description = " ".join(soundstatus)
  return True
