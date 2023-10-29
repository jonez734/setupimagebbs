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

def main(args, **kwargs):
  bbsengine.util.heading("save json file of setup data")
  
  setup = kwargs["setup"] if "setup" in kwargs else {}
  
  if ttyio.inputboolean("{var:promptcolor}save setup data? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y") is False:
    ttyio.echo("{var:normalcolor}setup data *not* {var:normalcolor}saved.{f6}")
    return True

  vice = kwargs["vice"] if "vice" in kwargs else {}
  
  tcpser = kwargs["tcpser"] if "tcpser" in kwargs else {}

  storage = setup["storage"] if "storage" in setup else {}

  data = {}

  data["setup"] = setup

#  data["setup"]["ioaddrs"] = ioaddrs

  data["setup"]["storage"] = {}
  for sd in storage:
    data["setup"]["storage"][sd.number] = sd.json()

  data["vice"] = {}
  for k, v in vice.items():
    data["vice"][k] = v

  data["tcpser"] = {}
  for k, v in tcpser.items():
    data["tcpser"][k] = v

#  if args.debug is True:
#    ttyio.echo("data=%r" % (data), interpret=False)

  default = os.path.join(args.basedir, "gfd3.json")
#  default = os.path.expandvars(default)
#  default = os.path.expanduser(default)

  filename = bbsengine.util.inputfilename("{var:promptcolor}save json filename: {var:inputcolor}", default, noneok=True, multiple=False, verify=None)
  if filename is None:
    ttyio.echo("aborted.")
    return True

  filename = os.path.expandvars(filename)
  filename = os.path.expanduser(filename)

  if os.path.exists(filename) is True:
    if ttyio.inputboolean(f"{{var:valuecolor}}{filename!r}{{var:promptcolor}} already exists. overwrite? {{var:optioncolor}}[y{{var:currentoptioncolor}}N{{var:optioncolor}}]{{var:promptcolor}}: {{var:inputcolor}}", "N") is False:
      ttyio.echo("{var:normalcolor}aborted.")
      return True

  if os.access(filename, os.W_OK|os.F_OK) is False:
    ttyio.echo(f"{filename!r} is not writable", level="error")
    return False

  fp = open(filename, "w")
  fp.write(json.dumps(data, sort_keys=True, indent=2)+"\n")
  fp.close()
  ttyio.echo(f"{{f6}}{{var:labelcolor}}saved to {{var:valuecolor}}{filename!r}{{/all}}")
  return True
