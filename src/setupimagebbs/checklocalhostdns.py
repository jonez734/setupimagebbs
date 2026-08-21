import socket

from bbsengine6 import io


def init(args, **kw):
    return True


def access(args, op, **kw):
    return True


def buildargs(args=None, **kw):
    return None


def main(args, **kw):
    #  lib.setarea("system: check for 'localhost' in dns")
    setup = kw["setup"] if "setup" in kw else {}

    io.echo("testing for localhost: ", flush=True, end="")

    try:
        res = socket.gethostbyname("localhost")
    except:
        io.echo(
            "dns check for 'localhost' failed, reverting to ipv4 address 127.0.0.1",
            level="warn",
        )
        setup["localhost"] = "127.0.0.1"
    #    return "127.0.0.1"
    else:
        io.echo("dns check for 'localhost' passed", level="success")
        setup["localhost"] = "localhost"
    #    return "localhost"
    return True
