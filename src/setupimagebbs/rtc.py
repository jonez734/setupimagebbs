from bbsengine6 import io


def init(args, **kw):
    return True


def access(args, op, **kw):
    return True


def buildargs(args, **kw):
    return None


def main(args, **kw):
    io.echo("rtc")
    return True
