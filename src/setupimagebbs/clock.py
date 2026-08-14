import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import lib

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args=None, **kw):
    return None

def main(args, **kwargs):
  bbsengine.util.heading("clock")
# clock1 = ds12c887rtc(args)
#  clock1 =  ttyio.inputboolean("use ds12c887rtc? [{bggray}{white}Y{/all}n]: ", "Y", "YN")
#  if clock1 is False:
  clock2 = ttyio.inputboolean("{var:promptcolor}use cmd fd-4000 RTC? {var:optioncolor}[y{var:currentoptioncolor}N{/all}{var:promptcolor}]: {var:inputcolor}", "N", "YN")
#  else:
#    clock2 = ttyio.inputboolean("use cmd fd-4000 RTC? [{bggray}{white}Y{/all}n]: ", "Y", "YN")

#  if clock1 is True and clock2 is True:
#    if ttyio.inputboolean("do you really want to use both the cmd rtc and ds12c887rtc? [yN]: ", "N", "YN") is False:
#      ttyio.echo("aborted", level="error")
#      return False

  status = []
  if clock2 is True:
    lib.runsubmodule(args, "cmd4000", **kw)
    status.append("cmd fd-4000rtc")
  if len(status) > 0:
    statusbuf = "(%s)" % (ttyio.readablelist(status))
  else:
    statusbuf = ""

  return (True, (status,)) # statusbuf)
