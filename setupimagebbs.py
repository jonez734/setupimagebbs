import locale
import argparse

import ttyio4 as ttyio
import bbsengine5 as bbsengine

vicecommandline = {}

def drivetype(args, devicenumber):
    pass

def main():
    # parser = OptionParser(usage="usage: %prog [options] projectid")
    parser = argparse.ArgumentParser("setupbbs")
    
    # parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    
    # parser.add_option("--debug", default=False, action="store_true", help="run %prog in debug mode")
    parser.add_argument("--debug", action="store_true", dest="debug")

    args = parser.parse_args()
    # ttyio.echo("args=%r" % (args), level="debug")

    locale.setlocale(locale.LC_ALL, "")

    terminalwidth = ttyio.getterminalwidth()
    bbsengine.inittopbar()
    if args is not None and "debug" in args and args.debug is True:
        ttyio.echo("setupbbs.main.100: args=%r" % (args))
    storage = ttyio.inputchar("[L]t Kernel or [C]MD? ", "LC", "")

    # x64sc.exe -cartcrt ltk.crt -ltkimage0 disk0.dlk -ltkimage1 disk1.dlk
    # -ltkimage2 disk2.dlk -drive8type 1541 -drive9type 0 -8 dos72-s1.d64
    # -kernal kernal

    vicecommandline = {}
    if storage == "L":
        ttyio.echo("Lt. Kernel")
        vicecommandline["-cartcrt"] = "ltk.crt"
        vicecommandline["-ltkimage0"] = "disk0.dlk"
        vicecommandline["-ltkimage1"] = "disk1.dlk"
        vicecommandline["-ltkimage2"] = "disk2.dlk"
    elif storage == "C":
        ttyio.echo("CMD")
        pass
    vicecommandline["-drive8type"] = "1541"
    vicecommandline["-drive9type"] = "0"
    vicecommandline["-8"] = "dos72-s1.d64"
    
    for k, v in vicecommandline.items():
        ttyio.echo("%s: %s" % (k, v))

    ttyio.echo("{reset}")
    return    

if __name__ == "__main__":
    main()
