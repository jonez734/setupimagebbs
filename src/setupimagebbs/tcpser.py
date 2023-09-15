def tcpser(args, **kwargs):
  bbsengine.setarea("tcpser")
  bbsengine.title("tcpser")

  acia1mode = vicecommandline["-acia1mode"] if "-acia1mode" in vicecommandline else None
  ttyio.echo("tcpser.120: acia1mode=%r" % (acia1mode), level="debug")

  if acia1mode == 1 or acia1mode == 2:
    speed = 38400
  else:
    speed = 2400

  tcpsercommandline["-s"] = ttyio.inputinteger("speed in bits per second (-s): ", speed)

  tcpsercommandline["-v"] = ttyio.inputinteger("tcp port for VICE RS232NET (-v): ", 25232)
  tcpsercommandline["-p"] = ttyio.inputstring("port or address:port (-p): ", "6400")

  tcpsercommandline["-i"] = ttyio.inputstring("modem init string (-i): at", "e0v0s0=1s2=27")

  bbsengine.title("tcpser: trace flags")

  traceflags = ""
  trace = []
  if ttyio.inputboolean("modem input (s) [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN") is True:
    traceflags += "s"
    trace += ["modem input"]
  if ttyio.inputboolean("modem output (S) [y{var:engine.currentoptioncolor}N{/all}]: ", "N", "YN") is True:
    traceflags += "S"
    trace += ["modem output"]
  if ttyio.inputboolean("IP input (i) [y{var:engine.currentoptioncolor}N{/all}]: ", "N", "YN") is True:
    traceflags += "i"
    trace += ["ip input"]
  if ttyio.inputboolean("IP output (I) [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN") is True:
    traceflags += "I"
    trace += ["ip output"]
  if len(traceflags) > 0:
    tcpsercommandline["-t"] = traceflags

  vocab = ["none", "fatal", "error", "warn", "info", "debug", "enter-exit", "all"]
  buf = ttyio.inputstring("Logging Level (-l): ", "all", completer=completeVocab(args, vocab), verify=verifyLoggingLevelName)
  level = None
  for i in range(0, len(vocab)):
    if vocab[i] == buf:
      level = i
      levelname = buf
      break

  if args is not None and args.debug is True:
    ttyio.echo("level=%r" % (level))

  tcpsercommandline["-l"] = level
  return (True, "logging: %s trace: %s speed: %s rs232net: %s port: %s" % (levelname, bbsengine.util.oxfordcomma(trace), tcpsercommandline["-s"], tcpsercommandline["-v"], tcpsercommandline["-p"]))
