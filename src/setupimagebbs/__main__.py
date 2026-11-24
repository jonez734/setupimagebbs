import argparse
import time
import locale

from bbsengine6 import io, screen
from . import lib

def main() -> None:
    """The setupimagebbs command: parse the arguments, start the screen, and run the main menu.

    The console script (pyproject.toml) and ``python -m setupimagebbs`` both run this.
    """
    parser = lib.buildargs(argparse.Namespace())
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
            "{savecursor}{curpos:%d,0}{el}{reset}{decrc}"
            % (io.getterminalheight())
        )


if __name__ == "__main__":
    main()
