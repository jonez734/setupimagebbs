import socket

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
#  lib.setarea("system: check for 'localhost' in dns")
  setup = kw["setup"] if "setup" in kw else {}
  
  ttyio.echo("testing for localhost: ", flush=True, end="")

  try:
    res = socket.gethostbyname("localhost")
  except:
    ttyio.echo("dns check for 'localhost' failed, reverting to ipv4 address 127.0.0.1", level="warn")
    setup["localhost"] = "127.0.0.1"
#    return "127.0.0.1"
  else:
    ttyio.echo("dns check for 'localhost' passed", level="success")
    setup["localhost"] = "localhost"
#    return "localhost"
  return True
