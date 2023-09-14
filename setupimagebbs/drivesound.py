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
