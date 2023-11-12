def oldstorage(args, **kwargs):
#  area("vice: storage")
#  title("vice: storage")

  useltk = setup["useltk"] if "useltk" in setup else True
  usecmd = setup["usecmd"] if "usecmd" in setup else False

  if useltk is True:
    ltk = ttyio.inputboolean("use ltk? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN")
  else:
    ltk = ttyio.inputboolean("use ltk? [y{bggray{white}N]: ", "N", "YN")
  if usecmd is True:
    cmd = ttyio.inputboolean("use cmd? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y", "YN")
  else:
    cmd = ttyio.inputboolean("use cmd? [y{bggray{white}N]: ", "N", "YN")

#  setup["useltk"] = ltk
#  setup["usecmd"] = cmd

  # handle hybrid!
  if ltk is True:
      ttyio.echo("Lt. Kernel")

#      setup["useltk"] = True
      ltkdevdefault = setup["ltkdev"] if "ltkdev" in setup else 8
      ltkdev = ttyio.inputinteger("ltk device number, 8..99: ", ltkdevdefault, verify=verifyLTKDevInRange)
      if ltkdev < 12 and ltkdev > 7:
        vicecommandline["-drive%dtype" % (ltkdev)] = "1581"

      setup["ltkdev"] = ltkdev
      vicecommandline["-cartcrt"] = bbsengine.inputfilename(args, "-cartcrt: ", os.path.join(args.basedir, "ltk.crt"), verify=bbsengine.verifyFileExistsReadable)
      vicecommandline["-ltkimage0"] = bbsengine.inputfilename(args, "-ltkimage0: ", os.path.join(args.basedir, "drive8-0.dlk"), verify=bbsengine.verifyFileExistsReadableWritable)
      vicecommandline["-ltkimage1"] = bbsengine.inputfilename(args, "-ltkimage1: ", os.path.join(args.basedir, "drive8-1.dlk"), verify=bbsengine.verifyFileExistsReadableWritable)
      vicecommandline["-ltkimage2"] = bbsengine.inputfilename(args, "-ltkimage2: ", os.path.join(args.basedir, "drive8-2.dlk"), verify=bbsengine.verifyFileExistsReadableWritable)
#      vicecommandline["-ltkimage3"] = inputfilename(args, "-ltkimage3: ", os.path.join(args.basedir, "drive8-3.dlk"), verify=verifyFileExistsReadableWritable)
#      vicecommandline["-ltkimage4"] = inputfilename(args, "-ltkimage4: ", os.path.join(args.basedir, "drive8-4.dlk"), verify=verifyFileExistsReadableWritable)
#      vicecommandline["-ltkimage5"] = inputfilename(args, "-ltkimage5: ", os.path.join(args.basedir, "drive8-5.dlk"), verify=verifyFileExistsReadableWritable)
#      vicecommandline["-ltkimage6"] = inputfilename(args, "-ltkimage6: ", os.path.join(args.basedir, "drive8-6.dlk"), verify=verifyFileExistsReadableWritable)
      vicecommandline["-ltkport"] = ttyio.inputinteger("Set LTK port number (0..15): ", 0, verify=verifyLTKPortInRange)

      # handle existing value
      ch = vicecommandline["-ltkio"] = ttyio.inputchar("Set LTK IO page (0: 0xDE00, {var:engine.currentoptioncolor}1: 0xDF00{/all}): ", "01", "1")
      if ch == "1":
        ttyio.echo("1: 0xDF00")
        ioaddrs["0xDF00"] = "ltkio"
        if "0xDE00" in ioaddrs and ioaddrs["0xDE00"] == "ltkio":
          del ioaddrs["0xDE00"]
      elif ch == "0":
        ttyio.echo("0: 0xDE00")
        ioaddrs["0xDE00"] = "ltkio"
        if "0xDF00" in ioaddrs and ioaddrs["0xDF00"] == "ltkio":
          del ioaddrs["0xDF00"]
      vicecommandline["-ltkio"] = ch

      ch = ttyio.inputboolean("use ltk dos72-s1 disk on device 9? [yN]: ", "N")
      if ch == "Y":
        vicecommandline["-9"] = os.path.join(args.basedir, "dos72-s1.d64")
        vicecommandline["-drive9type"] = "1541"
      elif ch == "N":
        ttyio.echo("No")
  if cmd is True:
#    setup["usecmd"] = True
    ttyio.echo("CMD")
    if "-ltkio" in vicecommandline and vicecommandline["-ltkio"] is not None and setup["ltkdev"] == 8:
      ttyio.echo("ltk assigned to drive %s" % (ltkdev))
      if ttyio.inputboolean("proceed? [yN]: ", "N", "YN") is True:
        vicecommandline["-8"] =  "dos-part1.dhd"
        vicecommandline["-drive8type"] = "4844"

    vicecommandline["-9"] =  "cmddrive9.d4m"
    vicecommandline["-drive9type"] = "4000"

    vicecommandline["-10"] = "cmddrive10.d4m"
    vicecommandline["-drive10type"] = "4000"

    vicecommandline["-11"] = "cmddrive11.d4m"
    vicecommandline["-drive11type"] = "4000"

  for drivenumber in range(8,11+1):
    default = None
    option = "-drive%dtype" % (drivenumber)
    #ttyio.echo("main.100: option=%r" % (option))
    #ttyio.echo("main.120: vicecommandline=%r" % (vicecommandline), interpret=False)
    if option in vicecommandline:
      default = vicecommandline[option]
    dt = drivetype(args, drivenumber, default)
    if dt is not None:
      vicecommandline[option] = dt

    dn = "drive%drtcsave" % (drivenumber)
    if dt == "4000" or dt == "2000" or dt == "4844":
      if ttyio.inputboolean("Enable saving of RTC data to drive %d? [{var:engine.currentoptioncolor}Y{/all}n]: " % (drivenumber), "Y", "YN") is True:
        vicecommandline["-%s" % (dn)] = None
        if "+%s" % (dn) in vicecommandline:
          del vicecommandline["+%s" % (dn)]
      else:
        vicecommandline["+%s" % (dn)] = None
        if "-%s" % (dn) in vicecommandline:
          del vicecommandline["-%s" % (dn)]

    default = None

    option = "-%d" % (drivenumber)

    if option in vicecommandline:
      default = vicecommandline[option]

    if dt != "0":
      if args.debug is True:
        ttyio.echo("storage.160: default=%r" % (default), level="debug")
      image = bbsengine.inputfilename(args, "drive %d image: " % (drivenumber), default, noneok=True, multiple=False)
      if image is not None:
        vicecommandline[option] = image

  result = []
  for r in range(8, 11+1):
    ttyio.echo("storage.120: r=%r" % (r))
    dt = "-drive%dtype" % (r)
    if dt in vicecommandline:
      v = vicecommandline[dt]
      if setup["useltk"] is True and "ltkdev" in setup and r == setup["ltkdev"]:
        result.append("%d: LTK (fallback: %s)" % (r, v))
      else:
        result.append("%d: %s" % (r, v))
  # ttyio.echo("storage.100: result=%r" % (result), interpret=False)
  return (True, " ".join(result))
