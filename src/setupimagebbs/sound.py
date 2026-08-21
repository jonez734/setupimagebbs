from bbsengine6 import io, util, menu
from . import lib


def init(args, **kw):
    return True


def buildargs(args, **kw):
    return None


def access(args, op, **kw):
    return True


def sync(args, **kw):
    vice = kw["vice"] if "vice" in kw else {}
    soundstatus = kw["soundstatus"] if "soundstatus" in kw else []

    menuitem = kw["menuitem"] if "menuitem" in kw else None

    status = []
    sync = vice["-soundsync"] if "-soundsync" in vice else "0"
    prompt = "{var:promptcolor}sync "
    if sync == "0":
        prompt += "{var:currentoptioncolor}0: system{/all} "
    else:
        prompt += "0: system "
    if sync == "1":
        prompt += "{var:currentoptioncolor}1: mono{/all} "
    else:
        prompt += "1: mono "
    if sync == "2":
        prompt += "{var:currentoptioncolor}2: stereo{/all}"
    else:
        prompt += "2: stereo"
    prompt += ": "
    ch = io.inputchar(prompt, "012", sync)
    vice["-soundsync"] = ch
    if ch == "0":
        io.echo("system")
        status.append("sync: system")
        description = "system"
    elif ch == "1":
        io.echo("mono")
        status.append("sync: mono")
        description = "mono"
    elif ch == "2":
        io.echo("stereo")
        status.append("sync: stereo")
        description = "stereo"
    soundstatus.append(" ".join(status))
    menuitem.description = description
    return True


def device(args, **kw):
    vice = kw["vice"] if "vice" in kw else {}
    device = vice["-sounddev"] if "-sounddev" in vice else "pulse"
    status = []
    soundstatus = kw["soundstatus"] if "soundstatus" in kw else []
    menuitem = kw["menuitem"] if "menuitem" in kw else None

    io.echo(f"sound.100: {device=}", level="debug")

    opts = []
    if device == "pulse":
        opts.append("{var:currentoptioncolor}[P]ulse{/all}")
        currentoption = "P"
    else:
        opts.append("[P]ulse")
    if device == "alsa":
        opts.append("{var:currentoptioncolor}[A]LSA{/all}")
        currentoption = "A"
    else:
        opts.append("[A]LSA")
    if device == "sdl":
        opts.append("{var:currentoptioncolor}[S]DL{/all}")
        currentoption = "S"
    else:
        opts.append("[S]DL")
    if device == "dummy":
        opts.append("{var:currentoptioncolor}[D]ummy{/all}")
        currentoption = "D"
    else:
        opts.append("[D]ummy")
    dev = io.inputchar("%s: " % (" ".join(opts)), "PASD", currentoption)
    if dev == "P":
        io.echo("Pulse")
        vice["-sounddev"] = "pulse"
        status.append("dev: pulse")
    elif dev == "A":
        io.echo("ALSA")
        vice["-sounddev"] = "alsa"
        status.append("dev: alsa")
    elif dev == "S":
        io.echo("SDL")
        vice["-sounddev"] = "sdl"
        status.append("dev: sdl")
    elif dev == "D":
        io.echo("Dummy")
        vice["-sounddev"] = "dummy"
        status.append("dev: dummy")
    soundstatus.append(" ".join(status))
    menuitem.description = " ".join(status)
    return True


def volume(args, **kw):
    soundstatus = kw["soundstatus"] if "soundstatus" in kw else []
    menuitem = kw["menuitem"] if "menuitem" in kw else None

    vice = kw["vice"] if "vice" in kw else {}

    volume = vice["-soundvolume"] if "-soundvolume" in vice else "70"
    vol = io.inputinteger(
        "{var:promptcolor}soundvolume {var:optioncolor}(0-100){var:promptcolor}: {var:inputcolor}",
        volume,
    )
    if vol > 100 or vol < 1:
        io.echo("volume out of range", level="error")
        return False

    vice["-soundvolume"] = vol
    soundstatus.append(f"{vol=}")
    menuitem.description = f"{vol=}"

    return True


def drivesound(args, **kw):
    vice = kw["vice"] if "vice" in kw else {}
    menuitem = kw["menuitem"] if "menuitem" in kw else None
    soundstatus = kw["soundstatus"] if "soundstatus" in kw else []
    drivesoundvolume = vice["-drivesoundvolume"] if "-drivesoundvolume" in vice else 73
    status = []
    if (
        io.inputboolean(
            "{var:promptcolor}Enable sound emulation of disk drives? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}",
            "Y",
        )
        is True
    ):
        volume = io.inputinteger(
            "{var:promptcolor}drive sound volume? {var:optioncolor}[0-100]{var:promptcolor}: {var:inputcolor}",
            drivesoundvolume,
        )
        if "+drivesound" in vice:
            del vice["+drivesound"]
        vice["-drivesound"] = None
        vice["-drivesoundvolume"] = volume
        menuitem.description = f"enabled, {volume=}"
    else:
        if "-drivesound" in vice:
            del vice["-drivesound"]
        if "-drivesoundvolume" in vice:
            del vice["-drivesoundvolume"]
        vice["+drivesound"] = None
        soundstatus.append("(disabled)")
        menuitem.description = "(disabled)"
    if "-drivesound" in vice:
        soundstatus.append(
            f"vol={vice['-drivesoundvolume']}"
        )  # % (vice["-drivesoundvolume"]))

    #  soundstatus.append("drivesound: vol=%s" % (vice["-drivesoundvolume"]))
    menuitem.status = True
    menuitem.description = f"{vice['-drivesoundvolume']=}"
    return True


def main(args, **kw):
    io.echo("sound")

    vice = kw["vice"] if "vice" in kw else {}

    soundstatus = []
    soundmenuitem = kw["menuitem"] if "menuitem" in kw else None

    util.heading("sound")

    if (
        io.inputboolean(
            "{var:promptcolor}enable sound? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}",
            "Y",
            "YN",
        )
        is False
    ):
        vice["+sound"] = None
        if "-sound" in vice:
            del vice["-sound"]
        menuitem.result = True
        menuitem.description = "(disabled)"
        #    soundstatus.append("(disabled)")
        return True

    if "+sound" in vice:
        del vice["+sound"]
    vice["-sound"] = None

    menuitems = [
        menu.Item("A", "sync", sync),
        menu.Item("B", "volume", volume),
        menu.Item("C", "device", device),
        menu.Item("D", "drive sound", drivesound),
    ]
    soundmenu = menu.Menu(args, "sound", menuitems, **kw)
    done = False
    while not done:
        op = soundmenu.run("sound: ")
        if op.menuitem.key == "X":
            io.echo("exit")
            break

        kw["menuitem"] = op.menuitem
        res = lib.runcallback(args, op.menuitem.module, soundstatus=soundstatus, **kw)
        soundmenuitem.description = " ".join(soundstatus)
    return True
