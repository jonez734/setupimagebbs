import ttyio6 as ttyio

def init(args, **kw):
    return True
    
def buildargs(args, **kw):
    return None

def access(args, op, **kw):
    return True

def main(args, **kw):
  bbsengine.setarea("vice: keyboard")
  bbsengine.title("keyboard")

  keyboards = ("0: Symbpolic", "1: Positional", "2: symbolic (user)", "3: positional (user)")
  ch = ttyio.inputchar("Specify index of keymap file ({var:engine.currentoptioncolor}0:symbolic{/all}, 1:positional, 2:symbolic (user), 3:positional (user))? [0123]: ","0123", "0")
  if ch == "0":
    resultbuf = "symbolic"
  elif ch == "1":
    resultbuf = "positional"
  elif ch == "2":
    resultbuf = "symbolic (user)"
  elif ch == "3":
    resultbuf = "positional (user)"
  else:
    resultbuf = ""

  vicecommandline["-keymap"] = ch
  return (True, resultbuf)
