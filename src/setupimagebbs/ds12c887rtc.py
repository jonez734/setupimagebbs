def ds12c887rtc(args, **kwargs):
  bbsengine.setarea("vice: ds12c887rtc")
  bbsengine.title("ds12c887rtc")
  if "-ds12c887rtc" in vicecommandline:
    ch = ttyio.inputboolean("Enable DS12C887RTC? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN")
  elif "+ds12c887rtc" in vicecommandline:
    ch = ttyio.inputboolean("Enable DS12C887RTC? [y{var:engine.currentoptioncolor}N{/all}]: ", "N", "YN")
  else:
    ch = ttyio.inputboolean("Enable DS12C887RTC? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN")

  if ch is False:
    vicecommandline["+ds12c887rtc"] = None
    if "-ds12c887rtc" in vicecommandline:
      del vicecommandline["-ds12c887rtc"]
    return True
  else:
    vicecommandline["-ds12c887rtc"] = None
    if "+ds12c887rtc" in vicecommandline:
      del vicecommandline["+ds12c887rtc"]

  if "-ds12c887rtcsave" in vicecommandline:
    ch = ttyio.inputboolean("Enable saving of the DS12C887RTC data when changed? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN")
  elif "+ds12c887rtcsave" in vicecommandline:
    ch = ttyio.inputboolean("Enable saving of the DS12C887RTC data when changed? [y{var:engine.currentoptioncolor}N{/all}]: ", "N", "YN")
  else:
    ch = ttyio.inputboolean("Enable saving of the DS12C887RTC data when changed? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN")

  if ch is False:
    vicecommandline["+ds12c887rtcsave"] = None
  else:
    vicecommandline["-ds12c887rtcsave"] = None

  addresschoices = ["0xD500","0xD600","0xD700", "0xDE00","0xDF00"]

  currentaddr = vicecommandline["-ds12c887rtcbase"] if "-ds12c887rtcbase" in vicecommandline else None

  defaultvalue = "0xD700"

  menu = []
  ch = ord("A")
  options = ""
  for c in addresschoices:
    i = ch - ord("A")
    if currentaddr == addresschoices[i] or defaultvalue == addresschoices[i]:
      menu.append("{var:engine.currentoptioncolor}[%s] %s{/all}" % (chr(ch), addresschoices[i]))
      defaultvalue = chr(ch)
    elif currentaddr in ioaddrs:
      menu.append("{darkgray}[%s] %s{/all}" % (chr(ch), addresschoices[i]))
    else:
      menu.append("[%s] %s" % (chr(ch), addresschoices[i]))
    options += chr(ch)
    ch += 1

  ch = ttyio.inputchar("ioaddr "+" ".join(menu)+": ", options, defaultvalue, noneok=False)
  addr = addresschoices[ord(ch) - ord("A")]
  ttyio.echo(addr)
  if addr in ioaddrs:
    if ttyio.inputboolean("that address is already used for %s. proceed? [y{var:engine.currentoptioncolor}N{/all}]: " % (ioaddrs[addr]), "N", "YN") is True:
      vicecommandline["-ds12c887rtcbase"] = addr
      ioaddrs[addr] = "ds12c887rtc"

  # -ds12c887rtchalted -> Set the RTC oscillator to 'halted'
  # -ds12c887rtcrunning -> Set the RTC oscillator to 'running'
  if "-ds12c887rtcrunning" in vicecommandline:
    ch = ttyio.inputchar("Set the RTC oscillator to {var:engine.currentoptioncolor}[R]unning{/all} or [H]alted: ", "RH", "R")
  elif "-ds12c887rtchalted" in vicecommandline:
    ch = ttyio.inputchar("Set the RTC oscillator to [R]unning or {var:engine.currentoptioncolor}[H]alted{/all}: ", "RH", "H")
  else:
    ch = ttyio.inputchar("Set the RTC oscillator to {var:engine.currentoptioncolor}[R]unning{/all} or [H]alted: ", "RH", "R")

  if ch == "R":
    ttyio.echo("Running")
    vicecommandline["-ds12c887rtcrunning"] = None
    if "-ds12c887rtchalted" in vicecommandline:
      del vicecommandline["-ds12c887rtchalted"]
  elif ch == "H":
    ttyio.echo("Halted")
    vicecommandline["-ds12c887rtchalted"] = None
    if "-ds12c887rtcrunning" in vicecommandline:
      del vicecommandline["-ds12c887rtcrunning"] 

  if ch is False:
    vicecommandline["-ds12c887running"] = None
    if "-ds12c887halted" in vicecommandline:
      del vicecommandline["-ds12c887halted"]
  else:
    vicecommandline["-ds12c887halted"] = None
    if "-ds12c887running" in vicecommandline:
      del vicecommandline["-ds12c887running"]

  ttyio.echo()
  return True
