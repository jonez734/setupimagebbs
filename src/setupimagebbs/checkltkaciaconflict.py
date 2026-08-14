import ttyio6 as ttyio

def init(args, **kw):
  return True

def access(args, op, **kw):
  return True

def buildargs(args, **kw):
  return None

def checkltkaciaconflict(args, **kw):
  vice = kw["vice"] if "vice" in kw else {}

  bbsengine.util.heading("vice: check for ltk / acia1 conflicts")

  ttyio.echo("check ltk and acia1 conflicts: ",end="")
  if "-aciabase" not in vice or "-ltkio" not in vice:
    ttyio.echo("OK. ltk or acia not defined.")
    return True

  if vice["-acia1base"] == vice["-ltkio"]:
      ttyio.echo("conflict.{f6}acia1base and ltkio are set to the same value (%s)" % (vice["-acia1base"]), level="error")
      return False
  return True
