import time
import locale

from bbsengine6 import io, screen
from . import lib

if __name__ == "__main__":
    parser = lib.buildargs()
    args = parser.parse_args()

    #    bbsengine.session.start(args)

    screen.init()

    locale.setlocale(locale.LC_ALL, "")
    time.tzset()

    lib.init(args)

    try:
        lib.runmodule(args, "main")
    except KeyboardInterrupt:
        io.echo("{restorecursor}{/all}*INTR*")
    except EOFError:
        io.echo("{restorecursor}{/all}*EOF*")
    finally:
        io.echo(
            "{savecursor}{curpos:%d,0}{el}{restorecursor}{reset}{/all}"
            % (io.getterminalheight())
        )
