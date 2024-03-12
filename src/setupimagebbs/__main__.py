import time
import locale

import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import module

if __name__ == "__main__":
    parser = module.buildargs()
    args = parser.parse_args()

#    bbsengine.session.start(args)

    bbsengine.screen.init()

    locale.setlocale(locale.LC_ALL, "")
    time.tzset()

    module.init(args)

    try:
        module.main(args)
    except KeyboardInterrupt:
        ttyio.echo("{restorecursor}{/all}*INTR*")
    except EOFError:
        ttyio.echo("{restorecursor}{/all}*EOF*")
    finally:
        ttyio.echo("{savecursor}{curpos:%d,0}{el}{restorecursor}{reset}{/all}" % (ttyio.getterminalheight()))
