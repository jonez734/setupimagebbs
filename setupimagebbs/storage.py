cbmtypes = {
  "1541":    "CBM 1541",
  "1542":    "CBM 1541-II",
  "1570":    "CBM 1570",
  "1571":    "CBM 1571",
  "1581":    "CBM 1581",
  "2031":    "CBM 2031",
  "8050":    "CBM 8050",
  "8250":    "CBM 8250"
}

class StorageDevice(object):
  def __init__(self, args, number, drivetype, **kwargs):
    self.args = args

    self.number = number
    self.type = drivetype
    self.hasrtc = False
    self.savertc = False
    self.usertc = False
    self.images = []

  def __str__(self):
    buf = "#% d %s" % (self.number, self.type)
    if self.usertc is True:
      buf += " rtc"
      if self.savertc is True:
        buf += ": saved"
    if self.cart is not None:
      buf += " cart: %s" % (self.cart)

    return buf
  def json(self):
    return {"number": self.number, "type": self.type, "hasrtc": self.hasrtc, "savertc": self.savertc, "usertc": self.usertc, "images": self.images}

#    return "#%d type: %s rtc: %s (%s) cart: %s fallbacktype: %s" % (self.number, self.type, self.rtc, self.savertc, self.cart, self.fallbacktype)

  def edit(self):
    self.type = drivetype(self.args, self.number)
    if self.type in ("4000", "4844", "RAMLINK", "2000"):
      if self.hasrtc is True:
        prompt = "use rtc? [{var:engine.currentoptioncolor}Y{/all}n]: "
        currentoption = "Y"
      else:
        prompt = "use rtc? [y{var:engine.currentoptioncolor}N{/all}]: "
        currentoption = "N"
      self.usertc = ttyio.inputboolean(prompt, currentoption)

      if self.savertc is True:
        prompt = "save rtc? [{var:engine.currentoptioncolor}Y{/all}n]: "
        currentoption = "Y"
      else:
        prompt = "save rtc? [y{var:engine.currentoptioncolor}N{/all}]: "
        currentoption = "N"
      self.savertc = ttyio.inputboolean(prompt, currentoption)
      # add device to rtc list
    return
  def save(self):
    result = {}
    pass

class StorageDeviceRAMLink(StorageDevice):
  def __init__(self, args, number, drivetype="RAMLINK"):
    super().__init__(args, number, drivetype)
    self.hasrtc = True
    self.args = args
    self.mode = 1
    self.cart = None
    self.size = 0
    self.enabled = False

  def edit(self):
    enableramlink = ttyio.inputboolean("enable ramlink? [yN]: ", "N")
    if enableramlink is False:
      vicecommandline["+ramlink"] = None
      for x in ("-ramlink", "-ramlinkmode", "-ramlinkrtcsave", "+ramlinkrtcsave", "-ramlinksize", "-ramlinkimage", "-ramlinkimagerw", "+ramlinkimagerw" ):
        if x in vicecommandline:
          del vicecommandline[x]
      return

    vicecommandline["-ramlink"] = None

    ramlinkmode = vicecommandline["-ramlinkmode"] if "-ramlinkmode" in vicecommandline else 1
    prompt = "-ramlinkmode ("
    if ramlinkmode == 1:
      prompt += "{var:engine.currentoptioncolor}1: Normal{/all} 0: Direct"
    else:
      prompt += "1: Normal {var:engine.currentoptioncolor}0: Direct{/all}"
    prompt += ") [01]: "
    ramlinkmode = ttyio.inputchar(prompt, "01", str(ramlinkmode))
    if ramlinkmode == "0":
      ttyio.echo("0: Direct")
    else:
      ttyio.echo("1: Normal")
    vicecommandline["-ramlinkmode"] = ramlinkmode

    size = ttyio.inputinteger("ramlink size in MiB (0=Disabled): ", 16)
    if size == 0:
      return (True, "disabled")
    self.size = size

    description = []
    vicecommandline["-ramlinksize"] = size
    description.append("[size: %s]" % (bbsengine.pluralize(size, "megabyte", "megabytes")))

    if ttyio.inputboolean("allow write to ramlink image? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y") is True:
        vicecommandline["-ramlinkimagerw"] = None
        description.append("[write image: Yes]")
        if "+ramlinkimagerw" in vicecommandline:
          del vicecommandline["+ramlinkimagerw"]
    else:
        vicecommandline["+ramlinkimagerw"] = None
        if "-ramlinkimagerw" in vicecommandline:
          del vicecommandline["-ramlinkimagerw"]
        description.append("[write image: No]")

    vicecommandline["-cartramlink"] = bbsengine.inputfilename(self.args, "cart ramlink bin: ", os.path.join(self.args.basedir, "ramlink.bin"), verify=bbsengine.verifyFileExistsReadable)

    vicecommandline["-ramlinkimage"] = bbsengine.inputfilename(self.args, "ramlink image: ", os.path.join(self.args.basedir, "ramlink.img"), verify=bbsengine.verifyFileExistsReadableWritable)

    ramlinkrtcsave = True if "-ramlinkrtcsave" in vicecommandline else False

    prompt = "ramlink rtc save? ["
    if ramlinkrtcsave is True:
      prompt += "{var:engine.currentoptioncolor}Y{/all}n"
    else:
      prompt += "y{var:engine.currentoptioncolor}N{/all}"
    prompt += "]: "
    if ramlinkrtcsave is True:
      default = "Y"
    else:
      default = "N"
    if ttyio.inputboolean(prompt, default) is True:
      vicecommandline["-ramlinkrtcsave"] = None
      if "+ramlinkrtcsave" in vicecommandline:
        del vicecommandline["+ramlinkrtcsave"]
      description.append("[rtc save: Yes]")
    else:
      vicecommandline["+ramlinkrtcsave"] = None
      if "-ramlinkcrtsave" in vicecommandline:
        del vicecommandline["-ramlinkrtcsave"]
      description.append("[rtc save: No]")

    self.enabled = True

    return (True, description)

  add = edit

  def __str__(self):
    if self.enabled is True:
      return "#%2d RAMLINK %dMB" % (self.number, self.size)
    return "#%2d RAMLINK (disabled)" % (self.number)

class StorageDeviceLTK(StorageDevice):
  def __init__(self, args, number, drivetype="LTK"):
    super().__init__(args, number, drivetype)
    self.type = drivetype
    self.hasrtc = False
    self.fallbacktype = None
    self.args = args
#    print("self.args=%r" % (self.args))
  def build(self):
    vicecommandline["-cartcrt"] = self.cartcrt
    vicecommandline["-ltkimage0"] = self.ltkimage0
    vicecommandline["-ltkimage1"] = self.ltkimage1
    vicecommandline["-ltkimage2"] = self.ltkimage2
    vicecommandline["-ltkport"] = self.ltkport
    return

  def json(self):
    res = super().json()
    res.update({ "cartcrt": self.cartcrt, "ltkimage0": self.ltkimage0, "ltkimage1": self.ltkimage1, "ltkimage2": self.ltkimage2, "fallbacktype": self.fallbacktype })
    return res

  def edit(self):
      cartcrt = vicecommandline["-cartcrt"] if "-cartcrt" in vicecommandline else os.path.join(self.args.basedir, "ltk.crt")
      self.cartcrt = bbsengine.inputfilename(self.args, "-cartcrt: ", cartcrt, verify=bbsengine.verifyFileExistsReadable)

      ltkimage0 = vicecommandline["-ltkimage0"] if "-ltkimage0" in vicecommandline else os.path.join(self.args.basedir, "drive8-0.dlk")
      ltkimage1 = vicecommandline["-ltkimage1"] if "-ltkimage1" in vicecommandline else os.path.join(self.args.basedir, "drive8-1.dlk")
      ltkimage2 = vicecommandline["-ltkimage2"] if "-ltkimage2" in vicecommandline else os.path.join(self.args.basedir, "drive8-2.dlk")
      self.ltkimage0 = bbsengine.inputfilename(self.args, "-ltkimage0: ", ltkimage0, verify=bbsengine.verifyFileExistsReadableWritable)
      self.ltkimage1 = bbsengine.inputfilename(self.args, "-ltkimage1: ", ltkimage1, verify=bbsengine.verifyFileExistsReadableWritable)
      self.ltkimage2 = bbsengine.inputfilename(self.args, "-ltkimage2: ", ltkimage2, verify=bbsengine.verifyFileExistsReadableWritable)

      ltkport = vicecommandline["-ltkport"] if "-ltkport" in vicecommandline else 0
      self.ltkport = ttyio.inputinteger("Set LTK port number (0..15): ", ltkport, verify=verifyLTKPortInRange)
      vicecommandline["-ltkport"] = self.ltkport

      ltkio = vicecommandline["-ltkio"] if "-ltkio" in vicecommandline else 1
      prompt = "Set LTK IO page ("
      if ltkio == "0":
        prompt += "{var:engine.currentoptioncolor}0: 0xDE00{/all}, 1: 0xDF00"
      elif ltkio == "1":
        prompt += "0: 0xDE00, {var:engine.currentoptioncolor}1: 0xDF00{/all}"
      prompt += "): "
      ch = vicecommandline["-ltkio"] = ttyio.inputchar(prompt, "01", "1")

      ttyio.echo("ch=%r" % (ch), level="debug")

      if ch == "1":
        ttyio.echo("1: 0xDF00")
        ioaddrs["0xDF00"] = "ltkio"
        if "0xDE00" in ioaddrs and ioaddrs["0xDE00"] == "ltkio":
          del ioaddrs["0xDE00"]
      elif ch == "0":
        ttyio.echo("0: 0xDE00")
        ttyio.echo("{f6}Warning: Using 0xDE00 for the LTK IO address is not supported by Image BBS 3.0.{f6}", level="warn")
        ioaddrs["0xDE00"] = "ltkio"
        if "0xDF00" in ioaddrs and ioaddrs["0xDF00"] == "ltkio":
          del ioaddrs["0xDF00"]
      vicecommandline["-ltkio"] = int(ch)

      if self.number > 11:
        ttyio.echo("fallback device disabled, #% d is greater than 11." % (self.number))
        return

      if ttyio.inputboolean("use ltk fallback device? [yN]: ", "N") is True:
        self.fallbacktype = ttyio.inputstring("fallback device (cbm only): ", "1581")
        vicecommandline["-drive%dtype" % (self.number)] = self.fallbacktype
        d = vicecommandline["-%d" % (self.number)] if "-%d" % (self.number) in vicecommandline else ""
        image = bbsengine.inputfilename(self.args, "fallback image name: ", d)
        if image is not None:
          vicecommandline["-%d" % (self.number)] = image
#          ttyio.echo("-%d set" % (self.number))

      vicecommandline["-ltkimage0"] = ltkimage0
      vicecommandline["-ltkimage1"] = ltkimage1
      vicecommandline["-ltkimage2"] = ltkimage2

      ttyio.echo("setting -kernal to 'kernal'")
      vicecommandline["-kernal"] = "kernal"
      return

  add = edit

  def __str__(self):
    buf = "#% d %s" % (self.number, self.type)
#    if self.cartcrt is not None:
#      buf += " cart: %s" % (self.cartcrt)
    if self.fallbacktype is not None:
      buf += " fallback: %s" % (self.fallbacktype)
    if "-ltkio" in vicecommandline:
      ltkio = vicecommandline["-ltkio"]
      if ltkio == 0:
        buf += " io: 0xDE00"
      elif ltkio == 1:
        buf += " io: 0xDF00"
      else:
        buf += " io: ERROR"
    if self.ltkport is not None:
      buf += " port: %d" % (self.ltkport)

    return buf

class StorageDeviceCBM(StorageDevice):
  def __init__(self, args, number, drivetype="CBM"):
    super().__init__(args, number, drivetype="CBM") # , data:dict={}, **kwargs)
    self.type = drivetype
    self.hasrtc = False
    self.number = number
    self.args = args
    self.image = ""

  def __str__(self):
    buf = "#% d %s" % (self.number, self.type)
    if self.image is not None:
      buf += " image: %s" % (self.image)
    return buf
  def json(self):
    result = super().json()
    res.update({ "image": self.image})
    return res

  def add(self):
    self.image = bbsengine.inputfilename(self.args, "image name: ", self.image)

  def edit(self):
    for k, v in cbmtypes.items():
      ttyio.echo("[%s] %s" % (k, v))
    t = ttyio.inputstring("type: ", self.type)
    if t not in cbmtypes:
      ttyio.echo("invalid drive type")
      return
    ttyio.echo("selected %s" % (cbmtypes[t]))
    self.type = t

    self.image = bbsengine.inputfilename(self.args, "image name: ", self.image)

class StorageDeviceCMD(StorageDevice):
  def __init__(self, args, number, devicetype="CMD"):
    super().__init__(args, number, devicetype) # , data:dict={}, **kwargs)
    self.hasrtc = True
    self.type = devicetype
    self.number = number
    self.image = ""
    self.bin = ""

  def edit(self, args):
    if self.hasrtc is True:
      if ttyio.inputboolean("use rtc? [Yn]: ", "Y") is True:
        self.usertc = True
        if ttyio.inputboolean("save rtc? [Yn]: ", "Y") is True:
          self.savertc = True
    self.image = bbsengine.inputfilename(self.args, "image filename: ", self.image)
    self.bin = bbsengine.inputfilename(self.args, "bin filename: ", self.bin)
    vicecommandline["-%d" % (self.number)] = self.image
    vicecommandline["-drive%dtype" % (self.number)] = self.type

  add = edit

  def __str__(self):
    buf = ""
    if self.usertc is True:
      buf += "rtc"
      if self.savertc is True:
        buf += " saved"
    return buf

class StorageDeviceREU(StorageDevice):
  def __init__(self, args):
    super().__init__(args) # , data:dict={}, **kwargs)

class StorageDevices(object):
  def __init__(self):
    self.devices = []
    self.subclasses = {
        "1001":    StorageDeviceCBM,
        "1540":    StorageDeviceCBM,
        "1541":    StorageDeviceCBM,
        "1542":    StorageDeviceCBM,
        "1570":    StorageDeviceCBM,
        "1571":    StorageDeviceCBM,
        "1581":    StorageDeviceCBM,
        "2031":    StorageDeviceCBM,
        "8050":    StorageDeviceCBM,
        "8250":    StorageDeviceCBM,
        "LTK":     StorageDeviceLTK,
        "2000":    StorageDeviceCMD,
        "4000":    StorageDeviceCMD,
        "4844":    StorageDeviceCMD,
        "RAMLINK": StorageDeviceRAMLink
    }

  def append(self, storagedevice):
    if issubclass(type(storagedevice), StorageDevice) is True:
      self.devices.append(storagedevice)
      return

    ttyio.echo("StorageDevices.append() not passed a subclass of StorageDevice")
    return

  def __getitem__(self, index):
    return self.devices[index]

  def find(self, number):
#    ttyio.echo("StorageDevices.find.number=%r" % (number), level="debug")
    for d in self.devices:
      if d.number == number:
        return d
    return None

  def clear(self):
    self.devices = []

  def __len__(self):
    return len(self.devices)

  def summary(self, args, **kwargs):
    if len(storagedevices) == 0:
      ttyio.echo("no storage devices configured.")
      return True
    for sd in storagedevices:
      ttyio.echo(str(sd))

    return True

  def add(self, args, **kwargs):
#    ttyio.echo("entering storagedevices.add()")
    number = ttyio.inputinteger("{var:engine.menu.promptcolor}device number: {var:engine.menu.inputcolor}")
    ttyio.echo("{/all}")
    dt = drivetype(args, number)

    subclass = self.subclasses[dt]
    sd = subclass(args, number, dt)
    sd.add()
    ttyio.echo(str(sd), level="debug")
    if self.find(number) is not None:
      ttyio.echo("#%d has already been defined." % (number))
      return False
    if ttyio.inputboolean("add this device? [{var:engine.currentoptioncolor}Y{/all}n]: {var:engine.menu.inputcolor}", "Y") is True:
      storagedevices.append(sd) # [storagedevice.device] = storagedevice
    else:
      ttyio.echo("storage device not added.")

    return False

  def edit(self, args, **kwargs):
#    ttyio.echo("edit{/all}")
    if len(storagedevices) == 0:
      ttyio.echo("no storage devices defined.", level="error")
      return False
    number = ttyio.inputinteger("device number: ")
    d = self.find(number)
    if d is None:
      ttyio.echo("device #%d is not defined" % (number), level="error")
      return False
    d.edit(args)
    return True

  def kill(self, args, **kwargs):
    ttyio.echo("kill")
    if len(storagedevices) == 0:
      ttyio.echo("no storage devices defined.", level="error")
      return False
    device = ttyio.inputinteger("kill which device?: ")
    if self.find(device) is None:
      ttyio.echo("unable to kill #%d as it has not been defined" % (device))
    if device is None or device == 0:
      ttyio.echo("no storage device number entered.")
      return False

    return False

