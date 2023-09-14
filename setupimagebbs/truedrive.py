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
