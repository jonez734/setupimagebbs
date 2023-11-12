import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import lib

def init(args, **kw):
  return True
  
def access(args, op, **kw):
  return True

def buildargs(args, **kw):
  return None

def main(args, **kw):
    vice = kw["vice"] if "vice" in kw else {}
    setup = kw["setup"] if "setup" in kw else {}
    ioaddrs = setup["ioaddrs"] if "ioaddrs" in kw else {}

    tcpser = kw["tcpser"] if "tcpser" in kw else {}

    bbsengine.util.heading("summary")
#    lib.setarea("summary")

#    bbsengine.screen.title("summary")

    if "-default" in vice:
        resetdefaults = True
        del vice["-default"]
    else:
        resetdefaults = False

    for k, v in ioaddrs.items():
        ttyio.echo(f"{k=} {v=}", level="debug")

    opts = []
    buf = ""

    if resetdefaults is True:
        opts.append("-default")

    for k, v in vice.items():
        if v is not None:
            buf = f"{k} {v}"
        else:
            buf = f"{k}"

        opts.append(buf)

    ttyio.echo("x64sc %s" % (" \\{f6} ".join(opts)), wordwrap=False)

    opts = []

    for k, v in tcpser.items():
        if v is not None:
            buf = "%s %s" % (k, v)
        else:
            buf = "%s" % (k)

        opts.append(buf)

    ttyio.echo("tcpser %s" % (" ".join(opts)))

    return True
