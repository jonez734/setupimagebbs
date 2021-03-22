import locale
import argparse

import ttyio4 as ttyio
import bbsengine5 as bbsengine

vicecommandline = {}

def updatetopbar(args, area):
    terminalwidth = bbsengine.getterminalwidth()
    bbsengine.updatetopbar("{bggray}{white}%s" % (area.ljust(terminalwidth-2)))
    return

def ramlink(args):
    if ttyio.inputboolean("use ramlink? ", "", "YN") is False:
        vicecommandline["-ramlink"] = None
        return

    vicecommandline["+ramlink"] = None
    if ttyio.inputboolean("rtc save? ", "", "YN") is True:
        vicecommandline["-rtcsave"] = None
    else:
        vicecommandline["+rtcsave"] = None
    return
    if ttyio.inputboolean("allow write to ramlink image? ", "Y", "YN") is True:
        vicecommandline["-ramlinkimagerw"] = None
    else:
        vicecommandline["+ramlinkimagerw"] = None
    ramlinksize = ttyio.inputinteger("RAMLINK RAMCARD size in MiB (0=Disabled): ")
    vicecommandline["-ramlinksize"] = ramlinksize
    return

def drivetype(args, devicenumber):
    types = {
        "1540": "CBM 1540",
        "1541": "CBM 1541",
        "1541-II": "CBM 1541-II",
        "1570": "CBM 1570",
        "1571": "CBM 1571",
        "1581": "CBM 1581"
    }
    options = "N"
    menu = {}
    char = ord("A")
    bbsengine.title("device %d setup" % (devicenumber))
    updatetopbar(args, "device %d setup" % (devicenumber))
    for k, v in types.items():
        ttyio.echo("[%s] %s" % (chr(char), v))
        options += chr(char)
        menu[chr(char)] = k
        char += 1
    ttyio.echo("[N] None")

    dt = ttyio.inputchar("device %d type: " % (devicenumber), options, "N")
    ttyio.echo("menu=%r" % (menu), interpret=False)
    if dt in menu:
        ttyio.echo("%s" % (menu[dt]))
        return menu[dt]
    return None

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

    if storage == "L":
        ttyio.echo("Lt. Kernel")
        vicecommandline["-cartcrt"] = "ltk.crt"
        vicecommandline["-ltkimage0"] = "disk0.dlk"
        vicecommandline["-ltkimage1"] = "disk1.dlk"
        vicecommandline["-ltkimage2"] = "disk2.dlk"
    elif storage == "C":
        ttyio.echo("CMD")
        pass
    # vicecommandline["-drive9type"] = "0"
    if storage == "L":
        if ttyio.inputboolean("use ltk dos72-s1 disk on device 8? ", "N", "YN"):
            vicecommandline["-8"] = "dos72-s1.d64"
            vicecommandline["-drive8type"] = "1541"
    
    device9type = drivetype(args, 9)
    if device9type is not None:
        vicecommandline["-device9type"] = device9type
        diskimage = ttyio.inputstring("device 9 disk: ", noneok=True)
    device10type = drivetype(args, 10)
    if device10type is not None:
        vicecommandline["-device10type"] = device10type
    device11type = drivetype(args, 11)
    if device11type is not None:
        vicecommandline["-device11type"] = device11type

    ramlink(args)

    for k, v in vicecommandline.items():
        if v is not None:
            ttyio.echo("%s: %s" % (k, v))
        else:
            ttyio.echo("%s" % (k))

    ttyio.echo("{reset}{/all}")
    return    

if __name__ == "__main__":
    main()
