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
  bbsengine.util.heading("vice: ramlink")

  vice = kw["vice"] if "vice" in kw else {}
  menuitem = kw["menuitem"] if "menuitem" in kw else None

  if "+ramlink" in vice:
    useramlink = True
    if "-ramlink" in vice:
      del vice["-ramlink"]
    prompt = "{var:promptcolor}use ramlink? {var:optioncolor}[Yn]: {var:inputcolor}"
    default = "Y"
    vice["+ramlink"] = None
  else:
    useramlink = False
    if "+ramlink" in vice:
      del vice["+ramlink"]
    prompt = "{var:promptcolor}use ramlink? {var:optioncolor}[yN]{var:promptcolor}: {var:inputcolor}"
    default = "N"

  if ttyio.inputboolean(prompt, default) is False:
    vice["-ramlink"] = None
    for x in ["+ramlink", "+ramlinkrtcsave", "-ramlinksize", "+ramlinksize", "-ramlinkimage", "-ramlinkimagerw", "+ramlinkimagerw", "-cartramlink"]:
      if x in vice:
        del vice[x]
    return (True, "disabled")

  description = []

#  device = ttyio.inputinteger("ramlink device: ", 16)
#  if device < 12:
#    ttyio.echo("ramlink device out of range (<12)")

  size = ttyio.inputinteger("{var:promptcolor}ramlink size in megabytes (0=Disabled): {var:inputcolor}", 16)
  if size == 0:
    menuitem.status = True
    menuitem.description = "(disabled)"
    return True

  vice["-ramlinksize"] = size
  description.append("[size: %s]" % (bbsengine.pluralize(size, "megabyte", "megabytes")))

  if ttyio.inputboolean("{var:promptcolor}allow write to ramlink image? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y") is True:
      vice["-ramlinkimagerw"] = None
      description.append("[write image: Yes]")
      if "+ramlinkimagerw" in vice:
        del vice["+ramlinkimagerw"]
  else:
      vice["+ramlinkimagerw"] = None
      if "-ramlinkimagerw" in vice:
        del vice["-ramlinkimagerw"]
      description.append("[write image: No]")

  vice["-cartramlink"] = bbsengine.inputfilename(args, "{var:promptcolor}cart ramlink bin: {var:inputcolor}", os.path.join(args.basedir, "ramlink.bin"), verify=bbsengine.verifyFileExistsReadable)

  vice["-ramlinkimage"] = bbsengine.inputfilename(args, "{var:promptcolor}ramlink image: {var:inputcolor}", os.path.join(args.basedir, "ramlink.img"), verify=bbsengine.verifyFileExistsReadableWritable)

  # handle pre-existing value!
  if ttyio.inputboolean("{var:promptcolor}ramlink rtc save? {var:optioncolor}[Yn]: ", "Y") is True:
    vice["-ramlinkrtcsave"] = None
    if "+ramlinkrtcsave" in vice:
      del vice["+ramlinkrtcsave"]
    description.append("[rtc save: Yes]")
  else:
    vice["+ramlinkrtcsave"] = None
    if "-ramlinkcrtsave" in vice:
      del vice["-ramlinkrtcsave"]
    description.append("[rtc save: No]")

  # handle pre-existing value!
  ramlinkmode = vice["-ramlinkmode"] if "-ramlinkmode" in vice else "1"
  prompt = "ramlinkmode ("
  if ramlinkmode == "1":
    prompt += "{var:currentoptioncolor}1=Normal{/all}, 0=Direct"
  else:
    prompt += "1=Normal, {var:currentoptioncolor}0=Direct{/all}"
  prompt += "): "
  ch = ttyio.inputchar(prompt, "01", ramlinkmode)
  if ch == "0":
    ttyio.echo("Direct")
    description.append("[mode: direct]")
  elif ch == "1":
    ttyio.echo("Normal")
    description.append("[mode: normal]")

  vice["-ramlinkmode"] = ch
  menuitem.description = " ".join(description)
  menuitem.status = True
  return (True, description)
