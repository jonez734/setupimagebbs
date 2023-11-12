import ttyio6 as ttyio
import bbsengine6 as bbsengine

def init(args, **kw):
  return True

def access(args, op, **kw):
  return True

def buildargs(args, **kw):
  return None

def main(args, **kw):
  vice = kw["vice"] if "vice" in kw else {}
  menuitem = kw["menuitem"] if "menuitem" in kw else None

  bbsengine.screen.setarea("vice: confirm before exit")

  if "-confirmonexit" in vice:
    confirmonexit = "Y"
  elif "+confirmonexit" in vice:
    confirmonexit = "N"
  else:
    confirmonexit = None

  prompt = "confirm before vice exit? ["
  if confirmonexit == "Y":
    prompt += "{var:currentoptioncolor}Y{var:optioncolor}n"
  else:
    prompt += "{var:optioncolor}y{var:currentoptioncolor}N"
  prompt += "{var:optioncolor}]{var:promptcolor}: {var:inputcolor}"
  if ttyio.inputboolean(prompt, confirmonexit) is True:
    vice["-confirmonexit"] = None
    if "+confirmonexit" in vice:
      del vice["+confirmonexit"]
    status = "Yes"
  else:
    vice["+confirmonexit"] = None
    if "-confirmonexit" in vice:
      del vice["-confirmonexit"]
    status = "No"

  menuitem.status = status
  return True
