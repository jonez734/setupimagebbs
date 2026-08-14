import re
import subprocess

import ttyio6 as ttyio
import bbsengine6 as bbsengine

def init(args, **kw):
  return True
  
def access(args, op, **kw):
  return True

def buildargs(args, **kw):
  return None
  
def getvicefeatures(args, filename:str="x64sc"):
  bbsengine.screen.setarea("vice - checking features")
#  title("vice: check")

  res = subprocess.run([filename, "--features"], capture_output=True, text=True)

  features = {}
  for match in re.finditer(r"^HAVE_(\S+)\s+(yes|no)\s+(.*)", res.stdout, re.MULTILINE):
#    ttyio.echo("match.groups()=%r" % (match.groups(),))
    feature = match.group(1)
    value = True if match.group(2) == "yes" else False
    # description = match.group(3)
    features[feature] = value # (value, description)
#    ttyio.echo("features[%s]=%r" % (feature, value))
  return features

  if define == "RS232NET":
    ttyio.echo("{bold}%s: %s (%s){/all}" % (description, value, define))
    if value is False:
      ttyio.echo("RS232NET is not enabled.", level="error")
      return False
    else:
      ttyio.echo("RS232NET is enabled", level="success")
      return True
  elif define == "IPV6":
    ttyio.echo("{bold}%s: %s (%s){/all}" % (description, value, define))
    if value is False:
      ttyio.echo("IPV6 is not enabled.", level="error")
      return False
    else:
      ttyio.echo("IPV6 is enabled", level="success")
      return True

  return None

def main(args, **kwargs):
#  bbsengine.setarea("checkvice")
  bbsengine.util.heading("check vice features")

  ttyio.echo("checkvice: ", end="", flush=True)
  features = getvicefeatures(args, args.x64scpath)
  ttyio.echo("OK")
  if "IPV6" in features and features["IPV6"] is True:
    ttyio.echo("IPV6 is enabled.")
  else:
    ttyio.echo("IPV6 is not enabled.")

  if "RS232NET" in features and features["RS232NET"] is True:
    ttyio.echo("RS232NET is enabled.", level="success")
    return True
  else:
    ttyio.echo("RS232NET is not enabled.", level="error")
    return False
