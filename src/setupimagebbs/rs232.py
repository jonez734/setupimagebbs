import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import lib

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args=None, **kw):
    return None

def main(args, **kw):
  ttyio.echo("rs232")

  menuitem = kw["menuitem"] if "menuitem" in kw else None
  tcpser = kw["tcpser"] if "tcpser" in kw else {}
  vice = kw["vice"] if "vice" in kw else {}
  setup = kw["setup"] if "setup" in kw else {}
  localhost = setup["localhost"] if "localhost" in setup else None

  bbsengine.util.heading("vice: rs232/ip232")

  dev = ttyio.inputinteger("{var:promptcolor}device {var:optioncolor}[1-4]{var:promptcolor}: {var:inputcolor}", 4)
  vice["+rsuser"] = None
  vice["-rsdev%d" % (dev)] = "%s:%s" % (localhost, tcpser["-v"])
  ip232 = ttyio.inputboolean("{var:promptcolor}enable ip232? {var:optioncolor}[Yn]{var:promptcolor}: ", "Y")
  vice["-rsdev%dip232" % (dev)] = ip232
  baud = ttyio.inputinteger("{var:promptcolor}baud rate: {var:inputcolor}", tcpser["-s"]) # 38400
  vice["-rsdev%dbaud" % (dev)] = baud

  if menuitem is not None:
    menuitem.result = True
    menuitem.description = f"[dev: {dev}] [ip232: {ip232}] [baud: {baud}]"
  return True
