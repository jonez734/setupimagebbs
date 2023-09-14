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
