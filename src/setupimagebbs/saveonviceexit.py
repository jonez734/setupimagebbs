from bbsengine6 import io
import bbsengine6 as bbsengine


def init(args, **kw):
    return True


def access(args, op, **kw):
    return True


def buildargs(args=None, **kw):
    return None


def main(args, **kwargs):
    bbsengine.util.heading("vice: save settings on vice exit")

    if "-saveres" in vicecommandline:
        saveres = "Y"
    elif "+saveres" in vicecommandline:
        saveres = "N"
    else:
        saveres = "Y"

    prompt = "save vice settings on exit? ["
    if saveres == "Y":
        prompt += "{var:engine.currentoptioncolor}Y{/all}n"
    else:
        prompt += "y{var:engine.currentoptioncolor}N{/all}"
    prompt += "]: "
    if io.inputboolean(prompt, saveres) is True:
        vicecommandline["-saveres"] = None
        if "+saveres" in vicecommandline:
            del vicecommandline["+saveres"]
        status = "Yes"
    else:
        vicecommandline["+saveres"] = None
        if "-saveres" in vicecommandline:
            del vicecommandline["-saveres"]
        status = "No"

    #  bbsengine.poparea()
    return (True, status)
