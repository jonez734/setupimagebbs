import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import lib
from . import module

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args=None, **kw):
    return None

def main(args, **kw):
  ttyio.echo("modem{f6}")

#  menuitem = kw["menuitem"] if "menuitem" in kw else None
#  setup = kw["setup"] if "setup" in kw else {}

  tcpser = kw["tcpser"] if "tcpser" in kw else {}

  menuitems = [
    bbsengine.menu.Item("A", "ACIA", "acia"),
    bbsengine.menu.Item("B", "TCPSER", "tcpser"),
    bbsengine.menu.Item("C", "RS232", "rs232", requires=("tcpser",)), # { "name": "rs232",  "module": "rs232",  "label": "RS232", "requires":("tcpser",)},
  ]
  menu = bbsengine.menu.Menu(args, "modem settings", menuitems)
  done = False
  while not done:
    res = menu.run("modem: ")
    if res.menuitem.key == "X":
      ttyio.echo("exit")
      break
    
    kw["menuitem"] = res.menuitem
    ttyio.echo(f"modem.100: {kw=}", level="debug")
    res = module.runsubmodule(args, res.menuitem.module, **kw) # setup=setup, vice=vice, **kw)
    ttyio.echo(f"modem.120: {kw=}", level="debug")
