import ttyio6 as ttyio

def init(args, **kw):
    return True
    
def buildargs(args, **kw):
    return None

def access(args, op, **kw):
    return True

def soundsync(args, **kwargs):
  status = []
  sync = vicecommandline["-soundsync"] if "-soundsync" in vicecommandline else "0"
  prompt = "sync "
  if sync == "0":
    prompt += "{var:engine.currentoptioncolor}0: system{/all} "
  else:
    prompt += "0: system "
  if sync == "1":
    prompt += "{var:engine.currentoptioncolor}1: mono{/all} "
  else:
    prompt += "1: mono "
  if sync == "2":
    prompt += "{var:engine.currentoptioncolor}2: stereo{/all}"
  else:
    prompt += "2: stereo"
  prompt += ": "
  ch = ttyio.inputchar(prompt, "012", sync)
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
  soundstatus.append(" ".join(status))
  return (True, status)

def sounddev(args, **kwargs):
  device = vicecommandline["-sounddev"] if "-sounddev" in vicecommandline else "pulse"
  status = []
  ttyio.echo("sound.100: device=%r" % (device), level="debug")

  opts = []
  if device == "pulse":
    opts.append("{var:engine.currentoptioncolor}[P]ulse{/all}")
    currentoption = "P"
  else:
    opts.append("[P]ulse")
  if device == "alsa":
    opts.append("{var:engine.currentoptioncolor}[A]LSA{/all}")
    currentoption = "A"
  else:
    opts.append("[A]LSA")
  if device == "sdl":
    opts.append("{var:engine.currentoptioncolor}[S]DL{/all}")
    currentoption = "S"
  else:
    opts.append("[S]DL")
  if device == "dummy":
    opts.append("{var:engine.currentoptioncolor}[D]ummy{/all}")
    currentoption = "D"
  else:
    opts.append("[D]ummy")
  dev = ttyio.inputchar("%s: " % (" ".join(opts)), "PASD", currentoption)
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
  soundstatus.append(" ".join(status))
  return (True, status)

def soundvolume(args, **kwargs):
  status = []
  volume = vicecommandline["-soundvolume"] if "-soundvolume" in vicecommandline else "70"
  vol = ttyio.inputinteger("soundvolume (0-100): ", volume)
  vicecommandline["-soundvolume"] = vol
  status.append("vol: %s" % (vol))
  soundstatus.append(" ".join(status))
  if vol > 100:
    return (False, status)
  return (True, status)

def drivesound(args, **kwargs):
    bbsengine.setarea("vice: drivesound")
    status = []
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
      status.append("(disabled)")
    if "-drivesound" in vicecommandline:
      status.append("vol=%s" % (vicecommandline["-drivesoundvolume"]))
    soundstatus.append("drivesound: vol=%s" % (vicecommandline["-drivesoundvolume"]))
    return (True, status)

def main(args, **kw):
  soundstatus = []

  bbsengine.setarea("sound", stack=True)
  if ttyio.inputboolean("enable sound? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN") is False:
    vicecommandline["+sound"] = None
    if "-sound" in vicecommandline:
      del vicecommandline["-sound"]
#    bbsengine.poparea()
    return (True, ("disabled"))

  if "+sound" in vicecommandline:
    del vicecommandline["+sound"]
  vicecommandline["-sound"] = None

  menuitems = [
    { "name": "soundsync",   "callback": soundsync,     "label": "sync"},
    { "name": "soundvolume", "callback": soundvolume,   "label": "volume"},
    { "name": "sounddev",    "callback": sounddev,      "label": "device"},
    { "name": "drivesound",  "callback": drivesound,    "label": "drive sound"},
  ]
  menu = bbsengine.Menu("sound", menuitems, args=args)
  menu.run("sound: ")
#  bbsengine.poparea()
  return (True, soundstatus)
