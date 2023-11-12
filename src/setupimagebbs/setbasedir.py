import ttyio6 as ttyio
import bbsengine6 as bbsengine

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
    
    ttyio.echo(f"{setup=}")

#    ttyio.echo(f"setbasedir.100: {mi=}", level="debug")

    basedir = setup["basedir"] if "basedir" in setup else args.basedir
    basedir = bbsengine.util.inputfilename("basedir: ", basedir, verify=bbsengine.util.verifyDirExistsWritable)
    setup["basedir"] = basedir
    
    if mi is not None:
        mi.result = True
#        mi.label = "CHANGED!"
        mi.description = "description goes here"
        ttyio.echo(f"setbasedir.120: {mi.status=}", level="debug")

    return True
#    return mi
