from bbsengine6 import io, util, input


def init(args, **kw):
    return True


def access(args, op, **kw):
    return True


def buildargs(args, **kw):
    return None


def main(args, **kw):
    setup = kw["setup"] if "setup" in kw else {}
    vice = kw["vice"] if "vice" in kw else {}
    mi = kw["menuitem"] if "menuitem" in kw else None

    io.echo(f"{setup=}")

    #    ttyio.echo(f"setbasedir.100: {mi=}", level="debug")

    basedir = setup["basedir"] if "basedir" in setup else args.basedir
    basedir = input.filename("basedir: ", basedir, verify=util.verify_dir_exists_writable)
    setup["basedir"] = basedir

    if mi is not None:
        mi.result = True
        #        mi.label = "CHANGED!"
        mi.description = "description goes here"
        io.echo(f"setbasedir.120: {mi.status=}", level="debug")

    return True


#    return mi
