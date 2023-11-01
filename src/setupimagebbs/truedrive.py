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
  bbsengine.util.heading("vice: truedrive")
  vice = kw["vice"] if "vice" in kw else {}
  if "-truedrive" in vice:
    defaultvalue = "Y"
  elif "+truedrive" in vice:
    defaultvalue = "N"
  else:
    defaultvalue = "Y"

  if defaultvalue == "Y":
    ch = ttyio.inputboolean("{var:promptcolor}truedrive? {var:optioncolor}[{var:currentoptioncolor}Y{var:optioncolor}n]{var:promptcolor}: {var:inputcolor}", "Y")
  else:
    ch = ttyio.inputboolean("{var:promptcolor}truedrive? {var:optioncolor}[y{var:currentoptioncolor}N{var:optioncolor}]{var:promptcolor}: {var:inputcolor}", "N")

  if ch is True:
    if "+truedrive" in vice:
      del vice["+truedrive"]
    vice["-truedrive"] = None
  else:
    if "-truedrive" in vice:
      del vice["-truedrive"]
    vice["+truedrive"] = None
