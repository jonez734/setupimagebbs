import ttyio6 as ttyio
import bbsengine6 as bbsengine

import storage

def init(args, **kw):
  return True

def access(args, op, **kw):
  return True

def buildargs(args, **kw):
  return None

def main(args, **kw):
  menuitem = kw["menuitem"] if "menuitem" in kw else None

  done = False
  while not done:
    bbsengine.util.heading("drive")
#    bbsengine.title("storage")
    ttyio.echo("[L]ist{f6}[A]dd{f6}[K]ill{f6}[E]dit{f6:2}[Q]uit{f6}")
    ch = ttyio.inputchar("{var:promptcolor}storage {var:optioncolor}[LAKEQ]{var:promptcolor}: {var:inputcolor}", "LAKEQ", "")
    if ch == "L":
      ttyio.echo("List{/all}")
      storagedevices.summary(args)
    elif ch == "A":
      ttyio.echo("Add{/all}")
      res = storagedevices.add(args)
    elif ch == "K":
      ttyio.echo("kill{/all}")
      res = storagedevices.kill(args)
    elif ch == "E":
      ttyio.echo("Edit{/all}")
      res = storagedevices.edit(args)
    elif ch == "Q":
      ttyio.echo("Quit{/all}")
      done = True
      break
  x = ""
  for sd in storagedevices:
    x += "%s " % (sd) # "% 2d: %s " % (sd.number, sd.type)
  return (True, x)
