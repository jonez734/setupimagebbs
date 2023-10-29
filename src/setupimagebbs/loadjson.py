import os
import json

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
#  global vicecommandline, tcpser, setup

#  vicecommandline = kwargs["vicecommandline"] if "vicecommandline" in kwargs else None

  setup = kw["setup"] if "setup" in kw else {}
  basedir = setup["basedir"] if "basedir" in setup else args.basedir
  vice = kw["vice"] if "vice" in kw else {}
  tcpser = kw["tcpser"] if "tcpser" in kw else {}
  
  filename = bbsengine.util.inputfilename("{var:promptcolor}load json filename: {var:inputcolor}", os.path.join(basedir, "gfd3.json"), verify=bbsengine.util.verifyFileExistsReadable, **kw)
  expandedfilename = os.path.expanduser(filename)
  expandedfilename = os.path.expandvars(expandedfilename)
  fp = open(expandedfilename, "r")
  data = json.loads(fp.read())
  ttyio.echo(f"loadjson.100: {data=}", level="debug")
  fp.close()
  if "vice" in data:
    vice = data["vice"]
    ttyio.echo(f"loadjson.120: {vice=}", level="debug")
  if "tcpser" in data:
    tcpser = data["tcpser"]
  if "setup" in data:
    setup = data["setup"]
  
  return (True, filename)
