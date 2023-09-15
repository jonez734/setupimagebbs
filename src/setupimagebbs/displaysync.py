def displaysync(args, **kwargs):
  resultbuf = ""
  def ntsc(args, **kwargs):
    vicecommandline["-ntsc"] = None
    if "-pal" in vicecommandline:
      del vicecommandline["-pal"]
    ttyio.echo(bbsengine.menuitemresults, level="debug")
    return (True, "NTSC")
  def pal(args, **kwargs):
    vicecommandline["-pal"] = None
    if "-ntsc" in vicecommandline:
      del vicecommandline["-ntsc"]
    return (True, "PAL")

  def preprompthook(args):
    bbsengine.setarea("vice: display")
    return

  bbsengine.title("vice: display")
  menuitems = [
    { "name": "displayntsc", "callback": ntsc, "label": "ntsc", "type":"radiobutton"},
    { "name": "displaypal",  "callback": pal,  "label": "pal",  "type":"radiobutton"},
  ]
  menu = bbsengine.Menu("display", menuitems, args=args)
  menu.run("display sync: ", preprompthook)
  return (True, resultbuf)

  sync = ttyio.inputchar("{var:engine.currentoptioncolor}[N]TSC{/all} or [P]AL? ", "NP", "N")
  if sync == "N":
    ttyio.echo("NTSC")
    vicecommandline["-ntsc"] = None
    if "-pal" in vicecommandline:
      del vicecommandline["-pal"]
    resultbuf = "NTSC"
  elif sync == "P":
    ttyio.echo("PAL")
    vicecommandline["-pal"] = None
    if "-ntsc" in vicecommandline:
      del vicecommandline["-ntsc"]
    resultbuf = "PAL"
  return (True, resultbuf)
