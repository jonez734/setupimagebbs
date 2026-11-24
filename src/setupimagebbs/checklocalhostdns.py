import socket
import argparse

from bbsengine6 import io


def init(args: argparse.Namespace, **kwargs) -> bool | None:
    return True


def access(args: argparse.Namespace, op: str, **kwargs) -> bool | None:
    return True


def buildargs(args: argparse.Namespace, **kwargs) -> argparse.ArgumentParser | None:
    return None


def main(args: argparse.Namespace, **kwargs) -> bool | None:
    #  lib.setarea("system: check for 'localhost' in dns")
    setup = kwargs["setup"] if "setup" in kwargs else {}

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
