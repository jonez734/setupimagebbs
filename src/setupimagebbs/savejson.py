import os
import json
import argparse

from bbsengine6 import io, util


def init(args: argparse.Namespace, **kwargs) -> bool | None:
    return True


def access(args: argparse.Namespace, op: str, **kwargs) -> bool | None:
    return True


def buildargs(args: argparse.Namespace, **kwargs) -> argparse.ArgumentParser | None:
    return None


def target_writable(filename: str) -> bool:
    """True when the save can be written: an existing file must be writable, and a new file needs a writable,
    existing directory to be created in. os.access() on a path that does not exist yet is False, so the check
    must look at the directory for a new file."""
    if os.path.exists(filename):
        return os.access(filename, os.W_OK)
    parent = os.path.dirname(os.path.abspath(filename))
    return os.path.isdir(parent) and os.access(parent, os.W_OK | os.X_OK)


def main(args: argparse.Namespace, **kwargs) -> bool | None:
    util.heading("save json file of setup data")

    setup = kwargs["setup"] if "setup" in kwargs else {}

    if (
        io.inputboolean(
            "{var:promptcolor}save setup data? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}",
            "Y",
        )
        is False
    ):
        io.echo("{var:normalcolor}setup data *not* {var:normalcolor}saved.{f6}")
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

    filename = util.inputfilename(
        args,
        "{var:promptcolor}save json filename: {var:inputcolor}",
        default,
        noneok=True,
        multiple=False,
        verify=None,
    )
    if filename is None:
        io.echo("aborted.")
        return True

    filename = os.path.expandvars(filename)
    filename = os.path.expanduser(filename)

    if os.path.exists(filename) is True:
        if (
            io.inputboolean(
                f"{{var:valuecolor}}{filename!r}{{var:promptcolor}} already exists. overwrite? {{var:optioncolor}}[y{{var:currentoptioncolor}}N{{var:optioncolor}}]{{var:promptcolor}}: {{var:inputcolor}}",
                "N",
            )
            is False
        ):
            io.echo("{var:normalcolor}aborted.")
            return True

    if not target_writable(filename):
        io.echo(f"{filename!r} is not writable", level="error")
        return False

    fp = open(filename, "w")
    fp.write(json.dumps(data, sort_keys=True, indent=2) + "\n")
    fp.close()
    io.echo(f"{{f6}}{{var:labelcolor}}saved to {{var:valuecolor}}{filename!r}{{/all}}")
    return True
