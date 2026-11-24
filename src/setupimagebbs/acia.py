import argparse
from bbsengine6 import io


def init(args: argparse.Namespace, **kwargs) -> bool | None:
    return True


def access(args: argparse.Namespace, op: str, **kwargs) -> bool | None:
    return True


def buildargs(args: argparse.Namespace, **kwargs) -> argparse.ArgumentParser | None:
    return None


def main(args: argparse.Namespace, **kwargs) -> bool | None:
    io.echo("ACIA settings{f6}")

    vice = kwargs["vice"] if "vice" in kwargs else {}
    ioaddrs = kwargs["ioaddrs"] if "ioaddrs" in kwargs else {}

    menuitem = kwargs["menuitem"] if "menuitem" in kwargs else None

    if (
        io.inputboolean(
            "{var:promptcolor}Enable the ACIA RS232 interface emulation (Swiftlink, Turbo232)? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}",
            "Y",
        )
        is False
    ):
        vice["+acia1"] = None
        for x in ["-acia1mode", "-acia1base", "-acia1irq", "-myaciadev", "-acia1"]:
            if x in vice:
                del vice[x]

        return True

    status = []

    # if acia1mode has already been set, use it, else "1" (swiftlink)
    acia1mode = vice["-acia1mode"] if "-acia1mode" in vice else 1
    if args.debug is True:
        io.echo(f"acia.100: {acia1mode=}", level="debug")

    # normal=2400, swiftlink=38400, turbo32=230400. image can handle up to 38400
    options = ["normal", "swiftlink", "turbo232"]
    prompt = []
    o = ""
    for i in range(0, len(options)):
        if acia1mode == i:
            prompt.append(
                "{var:currentoptioncolor}[%s] %s{/all}"
                % (chr(ord("A") + i), options[i])
            )
        else:
            prompt.append(
                "{var:optioncolor}[%s]{var:promptcolor} %s"
                % (chr(ord("A") + i), options[i])
            )
        o += chr(ord("A") + i)

    promptbuf = (
        "{var:promptcolor}set the ACIA mode %s: {var:optioncolor}[%s]{var:promptcolor}? {var:inputcolor}"
        % (" ".join(prompt), o)
    )
    ch = io.inputchar(promptbuf, o, chr(ord("A") + acia1mode))
    i = ord(ch) - ord("A")
    io.echo("%s" % (options[i]))
    status.append("mode: %s" % (options[i]))

    vice["-acia1mode"] = i

    # 0xDF00 is *not* supported by image ml30 without a recompile. 0xDF00 is used by LTK
    ioaddr = vice["-acia1base"] if "-acia1base" in vice else "0xDE00"
    io.echo("ioaddr=%s" % (ioaddr), level="debug")
    if ioaddr == "0xDF00":
        io.echo(
            "Warning: Image BBS 3.0 does not support 0xDF00 for the ACIA Cart",
            level="warn",
        )

    prompt = "Base address of the ACIA cartridge "
    if ioaddr == "0xDE00":
        prompt += "{var:currentoptioncolor}[A] 0xDE00{/all} {var:optioncolor}[b]{var:promptcolor} 0xDF00"
        default = "A"
    elif ioaddr == "0xDF00":
        prompt += "{var:currentoptioncolor}[a]{var:promptcolor} 0xDE00 {var:currentoptioncolor}[B] 0xDF00{/all}"
        default = "B"

    prompt += ": {var:optioncolor}[AB]{var:promptcolor}? {var:inputcolor}"
    ch = io.inputchar(prompt, "AB", default)
    if ch == "A":
        io.echo("0xDE00")
        vice["-acia1base"] = "0xDE00"
        ioaddrs["0xDE00"] = "acia1"
        status.append("io: 0xDE00")
    else:
        io.echo("0xDF00")
        vice["-acia1base"] = "0xDF00"
        ioaddrs["0xDF00"] = "acia1"
        status.append("io: 0xDF00 (UNSUPPORTED)")
        io.echo(
            "Warning: Image BBS 3.0 does not support address 0xDF00 for the ACIA Cart",
            level="warn",
        )

    prompt = "{var:promptcolor}Set the ACIA interrupt ("
    acia1irq = vice["-aciairq"] if "-aciairq" in vice else "1"
    if acia1irq == "0":
        prompt += "{var:currentoptioncolor}[0] None{/all}"
    else:
        prompt += "{var:optioncolor}[0]{var:promptcolor} None"

    if acia1irq == "1":
        prompt += " {var:currentoptioncolor}[1] NMI{/all}"
    else:
        prompt += " {var:optioncolor}[1]{var:promptcolor} NMI"

    if acia1irq == "2":
        prompt += " {var:currentoptioncolor}[2] IRQ{/all}"
    else:
        prompt += " {var:optioncolor}[2]{var:promptcolor} IRQ"
    prompt += ") [012]: "

    #  ttyio.echo("Warning: Image BBS 3.0 does not support 0xDF00 for the ACIA Cart", level="warn")
    #  ttyio.echo("acia1mode=%r" % (str(acia1mode)), level="debug")
    ch = io.inputchar(prompt, "012", str(acia1mode))
    if ch == "0":
        vice["-acia1irq"] = 0
        io.echo("0: None")
        status.append("interrupts: None")
    elif ch == "1":
        vice["-acia1irq"] = 1
        io.echo("1: NMI")
        status.append("interrupts: NMI")
    elif ch == "2":
        io.echo("2: IRQ")
        vice["-acia1irq"] = 2
        status.append("interrupts: IRQ")

    serialdev = int(vice["-myaciadev"]) if "-myaciadev" in vice else 4

    for s in range(1, 4 + 1):
        if int(serialdev) == s:
            io.echo(f"{{var:currentoptioncolor}}[{s}] serial {s}{{/all}}")
        else:
            io.echo(f"{{var:optioncolor}}[{s}]{{var:labelcolor}} serial {s}")

    ch = io.inputchar(
        "{var:promptcolor}acia device {var:optioncolor}[1234]{var:promptcolor}?: {var:inputcolor} ",
        "1234",
        "4",
    )
    n = ord(ch) - ord("0")
    if args.debug is True:
        io.echo(f"acia.100: {n=}", level="debug")
    vice["-myaciadev"] = n
    io.echo("serial%d" % (n))
    status.append("serial%d" % (n))
    # vicecommandline["-myaciadev"] = 3 # serial4
    vice["-acia1"] = None
    if args.debug is True:
        io.echo(f"acia.120: {status=}", level="debug")

    acia1base = vice["-acia1base"] if "-acia1base" in vice else "0xDE00"

    if acia1base != "0xDE00":
        menuitem.result = False
        menuitem.description = " ".join(status)
        return True

    menuitem.result = True
    menuitem.description = " ".join(status)
    return True
