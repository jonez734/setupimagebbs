def acia(args, **kwargs):
  bbsengine.setarea("vice: acia")
  bbsengine.title("vice: acia")

  if ttyio.inputboolean("Enable the ACIA RS232 interface emulation (Swiftlink, Turbo232)? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y") is False:
    vicecommandline["+acia1"] = None
    for x in ["-acia1mode", "-acia1base", "-acia1irq", "-myaciadev", "-acia1"]:
      if x in vicecommandline:
        del vicecommandline[x]

    return True

  status = []

  # if acia1mode has already been set, use it, else "1" (swiftlink)
  acia1mode = vicecommandline["-acia1mode"] if "-acia1mode" in vicecommandline else 1
  ttyio.echo("acia.100: acia1mode=%r" % (acia1mode), level="debug")

  # normal=2400, swiftlink=38400, turbo32=230400. image can handle up to 38400
  options = [ "normal", "swiftlink", "turbo232" ]
  prompt = []
  o = ""
  for i in range(0, len(options)):
    if acia1mode == i:
      prompt.append("{var:engine.currentoptioncolor}[%s] %s{/all}" % (chr(ord("A")+i), options[i]))
    else:
      prompt.append("[%s] %s" % (chr(ord("A")+i), options[i]))
    o += chr(ord("A")+i)

  promptbuf = "set the ACIA mode %s: [%s]? " % (" ".join(prompt), o)
  ch = ttyio.inputchar(promptbuf, o, chr(ord("A")+acia1mode))
  i = ord(ch) - ord("A")
  ttyio.echo("%s" % (options[i]))
  status.append("mode: %s" % (options[i]))

  vicecommandline["-acia1mode"] = i

  # 0xDF00 is *not* supported by image ml30 without a recompile. 0xDF00 is used by LTK
  ioaddr = vicecommandline["-acia1base"] if "-acia1base" in vicecommandline else "0xDE00"
  ttyio.echo("ioaddr=%s" % (ioaddr), level="debug")
  if ioaddr == "0xDF00":
    ttyio.echo("Warning: Image BBS 3.0 does not support 0xDF00 for the ACIA Cart", level="warn")

  prompt = "Base address of the ACIA cartridge "
  if ioaddr == "0xDE00":
    prompt += "{var:engine.currentoptioncolor}[A] 0xDE00{/all} [B] 0xDF00"
    default = "A"
  elif ioaddr == "0xDF00":
    prompt += "[A] 0xDE00 {var:engine.currentoptioncolor}[B] 0xDF00{/all}"
    default = "A"

  prompt += ": [AB]? "
  ch = ttyio.inputchar(prompt, "AB", default)
  if ch == "A":
    ttyio.echo("0xDE00")
    vicecommandline["-acia1base"] = "0xDE00"
    ioaddrs["0xDE00"] = "acia1"
    status.append("io: 0xDE00")
  else:
    ttyio.echo("0xDF00")
    vicecommandline["-acia1base"] = "0xDF00"
    ioaddrs["0xDF00"] = "acia1"
    status.append("io: 0xDF00")
    ttyio.echo("Warning: Image BBS 3.0 does not support address 0xDF00 for the ACIA Cart", level="warn")

  prompt = "Set the ACIA interrupt ("
  acia1irq = vicecommandline["-aciairq"] if "-aciairq" in vicecommandline else "1"
  if acia1irq == "0":
    prompt += "{var:engine.currentoptioncolor}[0] None{/all}"
  else:
    prompt += "[0] None"

  if acia1irq == "1":
    prompt += " {var:engine.currentoptioncolor}[1] NMI{/all}"
  else:
    prompt += " [1] NMI"

  if acia1irq == "2":
    prompt += " {var:engine.currentoptioncolor}[2] IRQ{/all}"
  else:
    prompt += " [2] IRQ"
  prompt += ") [012]: "

#  ttyio.echo("Warning: Image BBS 3.0 does not support 0xDF00 for the ACIA Cart", level="warn")
#  ttyio.echo("acia1mode=%r" % (str(acia1mode)), level="debug")
  ch = ttyio.inputchar(prompt, "012", str(acia1mode))
  if ch == "0":
    vicecommandline["-acia1irq"] = 0
    ttyio.echo("0: None")
    status.append("interrupts: None")
  elif ch == "1":
    vicecommandline["-acia1irq"] = 1
    ttyio.echo("1: NMI")
    status.append("interrupts: NMI")
  elif ch == "2":
    ttyio.echo("2: IRQ")
    vicecommandline["-acia1irq"] = 2
    status.append("interrupts: IRQ")

  serialdev = int(vicecommandline["-myaciadev"]) if "-myaciadev" in vicecommandline else 4

  for s in range(1,4+1):
    if int(serialdev) == s:
      ttyio.echo("{var:engine.currentoptioncolor}[%d] serial %d{/all}" % (serialdev, serialdev))
    else:
      ttyio.echo("[%d] serial %d" % (s, s))

  prompt = "acia device [1234]: "
  ch = ttyio.inputchar(prompt, "1234", "4")
  n = ord(ch) - ord("0")
  ttyio.echo("acia.100: n=%d" % (n), level="debug")
  vicecommandline["-myaciadev"] = n
  ttyio.echo("serial%d" % (n))
  status.append("serial%d" % (n))
  # vicecommandline["-myaciadev"] = 3 # serial4
  vicecommandline["-acia1"] = None
  ttyio.echo("acia.120: status=%r" % (status), interpret=False, level="debug")

  acia1base = vicecommandline["-acia1base"] if "-acia1base" in vicecommandline else "0xDE00"

  if acia1base != "0xDE00":
    return (False, status)
  return (True, status) # (True, status) # "("+" ".join(status)+")")
