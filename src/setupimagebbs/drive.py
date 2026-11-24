from bbsengine6 import io
import bbsengine6 as bbsengine


def init(args, **kw):
    return True


def access(args, op, **kw):
    return True


def buildargs(args, **kw):
    return None


def main(args, **kw):
    menuitem = kw["menuitem"] if "menuitem" in kw else None

    done = False
    while not done:
        bbsengine.util.heading("drive")
        #    bbsengine.title("storage")
        io.echo("[L]ist{f6}[A]dd{f6}[K]ill{f6}[E]dit{f6:2}[Q]uit{f6}")
        ch = io.inputchar(
            "{var:promptcolor}storage {var:optioncolor}[LAKEQ]{var:promptcolor}: {var:inputcolor}",
            "LAKEQ",
            "",
        )
        if ch == "L":
            io.echo("List{/all}")
            storagedevices.summary(args)
        elif ch == "A":
            io.echo("Add{/all}")
            res = storagedevices.add(args)
        elif ch == "K":
            io.echo("kill{/all}")
            res = storagedevices.kill(args)
        elif ch == "E":
            io.echo("Edit{/all}")
            res = storagedevices.edit(args)
        elif ch == "Q":
            io.echo("Quit{/all}")
            done = True
            break
    x = ""
    for sd in storagedevices:
        x += "%s " % (sd)  # "% 2d: %s " % (sd.number, sd.type)
    return (True, x)
