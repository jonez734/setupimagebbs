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
  bbsengine.util.heading("vice: ramlink")

  if "+ramlink" in vicecommandline:
    useramlink = True
    if "-ramlink" in vicecommandline:
      del vicecommandline["-ramlink"]
    prompt = "{var:promptcolor}use ramlink? {var:optioncolor}[Yn]: {var:inputcolor}"
    default = "Y"
    vicecommandline["+ramlink"] = None
  else:
    useramlink = False
    if "+ramlink" in vicecommandline:
      del vicecommandline["+ramlink"]
    prompt = "{var:promptcolor}use ramlink? {var:optioncolor}[yN]{var:promptcolor}: {var:inputcolor}"
    default = "N"

  if ttyio.inputboolean(prompt, default) is False:
    vicecommandline["-ramlink"] = None
    for x in ["+ramlink", "+ramlinkrtcsave", "-ramlinksize", "+ramlinksize", "-ramlinkimage", "-ramlinkimagerw", "+ramlinkimagerw", "-cartramlink"]:
      if x in vicecommandline:
        del vicecommandline[x]
    return (True, "disabled")

  description = []

#  device = ttyio.inputinteger("ramlink device: ", 16)
#  if device < 12:
#    ttyio.echo("ramlink device out of range (<12)")

  size = ttyio.inputinteger("{var:promptcolor}ramlink size in megabytes (0=Disabled): {var:inputcolor}", 16)
  if size == 0:
    return (True, "disabled")

  vicecommandline["-ramlinksize"] = size
  description.append("[size: %s]" % (bbsengine.pluralize(size, "megabyte", "megabytes")))

  if ttyio.inputboolean("{var:promptcolor}allow write to ramlink image? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y") is True:
      vicecommandline["-ramlinkimagerw"] = None
      description.append("[write image: Yes]")
      if "+ramlinkimagerw" in vicecommandline:
        del vicecommandline["+ramlinkimagerw"]
  else:
      vicecommandline["+ramlinkimagerw"] = None
      if "-ramlinkimagerw" in vicecommandline:
        del vicecommandline["-ramlinkimagerw"]
      description.append("[write image: No]")

  vicecommandline["-cartramlink"] = bbsengine.inputfilename(args, "{var:promptcolor}cart ramlink bin: {var:inputcolor}", os.path.join(args.basedir, "ramlink.bin"), verify=bbsengine.verifyFileExistsReadable)

  vicecommandline["-ramlinkimage"] = bbsengine.inputfilename(args, "{var:promptcolor}ramlink image: {var:inputcolor}", os.path.join(args.basedir, "ramlink.img"), verify=bbsengine.verifyFileExistsReadableWritable)

  # handle pre-existing value!
  if ttyio.inputboolean("{var:promptcolor}ramlink rtc save? {var:optioncolor}[Yn]: ", "Y") is True:
    vicecommandline["-ramlinkrtcsave"] = None
    if "+ramlinkrtcsave" in vicecommandline:
      del vicecommandline["+ramlinkrtcsave"]
    description.append("[rtc save: Yes]")
  else:
    vicecommandline["+ramlinkrtcsave"] = None
    if "-ramlinkcrtsave" in vicecommandline:
      del vicecommandline["-ramlinkrtcsave"]
    description.append("[rtc save: No]")

  # handle pre-existing value!
  ramlinkmode = vicecommandline["-ramlinkmode"] if "-ramlinkmode" in vicecommandline else "1"
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

  vicecommandline["-ramlinkmode"] = ch
  return (True, description)
