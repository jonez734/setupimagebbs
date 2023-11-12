def oldsound(args, **kwargs):
  bbsengine.setarea("sound")
  status = []
  if ttyio.inputboolean("enable sound? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN") is False:
    vicecommandline["+sound"] = None
    if "-sound" in vicecommandline:
      del vicecommandline["-sound"]
    return (True, ("disabled"))

  if "+sound" in vicecommandline:
    del vicecommandline["+sound"]
  vicecommandline["-sound"]
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
