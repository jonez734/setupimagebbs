import ttyio6 as ttyio
import bbsengine6 as bbsengine

class completeVocab(object):
  def __init__(self, args, vocab):
      # ttyio.echo("completeAttributeName.100: called")
      self.vocab = vocab

  # @log_exceptions
  def complete(self:object, text:str, state:int):
    results = [x for x in self.vocab if x.startswith(text)] + [None]
    return results[state]

def verifyLoggingLevelName(buf, **kw):
  vocab = ["none", "fatal", "error", "warn", "info", "debug", "enter-exit", "all"]
  if buf in vocab:
    return True
  return False

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args=None, **kw):
    return None

def main(args, **kw):
  ttyio.echo("tcpser{f6}")

  bbsengine.util.heading("tcpser")

  menuitem = kw["menuitem"] if "menuitem" in kw else None

  tcpser = kw["tcpser"] if "tcpser" in kw else {}
  vice = kw["vice"] if "vice" in kw else {}

  acia1mode = vice["-acia1mode"] if "-acia1mode" in vice else None
  if args.debug is True:
    ttyio.echo(f"tcpser.120: {acia1mode=}", level="debug")

  if acia1mode == 1 or acia1mode == 2:
    speed = 38400
  else:
    speed = 2400

  tcpser["-s"] = ttyio.inputinteger("{var:promptcolor}speed in bits per second (-s): {var:inputcolor}", speed)

  tcpser["-v"] = ttyio.inputinteger("{var:promptcolor}tcp port for VICE RS232NET (-v): {var:inputcolor}", 25232)
  tcpser["-p"] = ttyio.inputstring("{var:promptcolor}port or address:port (-p): {var:inputcolor}", "6400")

  tcpser["-i"] = ttyio.inputstring("{var:promptcolor}modem init string (-i): {var:inputcolor}at", "e0v0s0=1s2=27")

  ttyio.echo()

  traceflags = ""
  trace = []
  if ttyio.inputboolean("{var:promptcolor}modem input (s) {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y") is True:
    traceflags += "s"
    trace += ["modem input"]
  if ttyio.inputboolean("{var:promptcolor}modem output (S) {var:optioncolor}[yN]{var:promptcolor}: {var:inputcolor}", "N") is True:
    traceflags += "S"
    trace += ["modem output"]
  if ttyio.inputboolean("{var:promptcolor}IP input (i) {var:optioncolor}[yN]{var:promptcolor}: {var:inputcolor}", "N") is True:
    traceflags += "i"
    trace += ["ip input"]
  if ttyio.inputboolean("{var:promptcolor}IP output (I) {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y") is True:
    traceflags += "I"
    trace += ["ip output"]
  if len(traceflags) > 0:
    tcpser["-t"] = traceflags

  ttyio.echo()
  if args.debug is True:
    ttyio.echo(f"tcpser.140: {tcpser=}", level="debug")

  vocab = ["none", "fatal", "error", "warn", "info", "debug", "enter-exit", "all"]
  buf = ttyio.inputstring("{var:promptcolor}Logging Level (-l): {var:inputcolor}", "all", completer=completeVocab(args, vocab), verify=verifyLoggingLevelName)
  level = None
  for i in range(0, len(vocab)):
    if vocab[i] == buf:
      level = i
      levelname = buf
      break

  if args is not None and args.debug is True:
    ttyio.echo(f"{level=}")

  menuitem.result = True
  menuitem.description = f"logging: {levelname} trace: {' '.join(trace)} speed: {tcpser['-s']} rs232net: {tcpser['-v']} port: {tcpser['-p']}"
  tcpser["-l"] = level

  ttyio.echo(f"tcpser.160: {tcpser=}", level="debug")
  kw["tcpser"] = tcpser

  ttyio.echo(f"tcpser.180: {kw=}", level="debug")

  return True
#  return (True, "logging: %s trace: %s speed: %s rs232net: %s port: %s" % (levelname, bbsengine.util.oxfordcomma(trace), tcpser["-s"], tcpser["-v"], tcpser["-p"]))
