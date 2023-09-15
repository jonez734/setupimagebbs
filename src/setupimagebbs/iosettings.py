def iosettings(args, **kwargs):
  bbsengine.title("iocollision handling")
  iocollision = vicecommandline["-iocollision"] if "-iocollision" in vicecommandline else 0

  if iocollision == 0:
    ttyio.echo("{var:engine.currentoptioncolor}[0] error message, detatch all involved carts{/all}")
  else:
    ttyio.echo("[0] error message, detatch all involved carts")

  if iocollision == 1:
    ttyio.echo("{var:engine.currentoptioncolor}[1] error message, detach most recent involved cart{/all}")
  else:
    ttyio.echo("[1] error message, detach most recent involved cart")
  
  if iocollision == 2:
    ttyio.echo("{var:engine.currentoptioncolor}[2] warning in log, bitwise-and valid return values{/all}")
  else:
    ttyio.echo("[2] warning in log, bitwise-and valid return values")

  ch = ttyio.inputchar("iocollision handling [012]: ", "012", str(iocollision))
  if ch == "0":
    ttyio.echo("0: detach all involved carts")
  elif ch == "1":
    ttyio.echo("1: detach most recent involved cart")
  elif ch == "2":
    ttyio.echo("2: warn, bitwise-and valid return values")
  vicecommandline["-iocollision"] = int(ch)
  return True
