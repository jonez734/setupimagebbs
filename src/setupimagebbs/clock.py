from bbsengine6 import io
import bbsengine6 as bbsengine

from . import lib


def _readable_list(items):
    """Join items as "a", "a and b", or "a, b and c" (the status line's plain form, no colour codes)."""
    items = [str(i) for i in items]
    if len(items) <= 2:
        return " and ".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


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
    clock2 = io.inputboolean(
        "{var:promptcolor}use cmd fd-4000 RTC? {var:optioncolor}[y{var:currentoptioncolor}N{/all}{var:promptcolor}]: {var:inputcolor}",
        "N",
        "YN",
    )
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
        statusbuf = "(%s)" % (_readable_list(status))
    else:
        statusbuf = ""

    return (True, (status,))  # statusbuf)
