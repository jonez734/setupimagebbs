import re
import subprocess

from bbsengine6 import io, screen, util


def init(args, **kw):
    return True


def access(args, op, **kw):
    return True


def buildargs(args, **kw):
    return None


def getvicefeatures(args, filename: str = "x64sc"):
    screen.setarea("vice - checking features")
    #  title("vice: check")

    res = subprocess.run([filename, "--features"], capture_output=True, text=True)

    features = {}
    for match in re.finditer(
        r"^HAVE_(\S+)\s+(yes|no)\s+(.*)", res.stdout, re.MULTILINE
    ):
        #    ttyio.echo("match.groups()=%r" % (match.groups(),))
        feature = match.group(1)
        value = True if match.group(2) == "yes" else False
        # description = match.group(3)
        features[feature] = value  # (value, description)
    #    ttyio.echo("features[%s]=%r" % (feature, value))
    return features

    if define == "RS232NET":
        io.echo("{bold}%s: %s (%s){/all}" % (description, value, define))
        if value is False:
            io.echo("RS232NET is not enabled.", level="error")
            return False
        else:
            io.echo("RS232NET is enabled", level="success")
            return True
    elif define == "IPV6":
        io.echo("{bold}%s: %s (%s){/all}" % (description, value, define))
        if value is False:
            io.echo("IPV6 is not enabled.", level="error")
            return False
        else:
            io.echo("IPV6 is enabled", level="success")
            return True

    return None


def main(args, **kwargs):
    #  bbsengine.setarea("checkvice")
    util.heading("check vice features")

    io.echo("checkvice: ", end="", flush=True)
    features = getvicefeatures(args, args.x64scpath)
    io.echo("OK")
    if "IPV6" in features and features["IPV6"] is True:
        io.echo("IPV6 is enabled.")
    else:
        io.echo("IPV6 is not enabled.")

    if "RS232NET" in features and features["RS232NET"] is True:
        io.echo("RS232NET is enabled.", level="success")
        return True
    else:
        io.echo("RS232NET is not enabled.", level="error")
        return False
