import ttyio6 as ttyio
import bbsengine6 as bbsengine

def drivetype(args, devicenumber, oldvalue=None):
# 1540: CBM 1540,
# 1541: CBM 1541,
# 1542: CBM 1541-II,
# 1570: CBM 1570,
# 1571: CBM 1571,
# 1581: CBM 1581,
# 2000: CMD FD-2000,
# 4000: CMD FD-4000,
# 4844: CMD HD,
# 2031: CBM 2031,
# 2040: CBM 2040,
# 3040: CBM 3040,
# 4040: CBM 4040,
# 1001: CBM 1001,
# 8050: CBM 8050,
# 8250: CBM 8250

#    types = {
#        "1001":    ("CBM 1001", StorageDeviceCBM),
#        "1540":    ("CBM 1540", StorageDeviceCBM),
#        "1541":    ("CBM 1541", StorageDeviceCBM),
#        "1542":    ("CBM 1541-II", StorageDeviceCBM),
#        "1570":    ("CBM 1570", StorageDeviceCBM),
#        "1571":    ("CBM 1571", StorageDeviceCBM),
#        "1581":    ("CBM 1581", StorageDeviceCBM),
#        "2031":    ("CBM 2031", StorageDeviceCBM),
#        "8050":    ("CBM 8050", StorageDeviceCBM),
#        "8250":    ("CBM 8250", StorageDeviceCBM),
#        "LTK":     ("Lt. Kernal", StorageDeviceLTK),
#        "2000":    ("CMD FD-2000", StorageDeviceCMD),
#        "4000":    ("CMD FD-4000", StorageDeviceCMD),
#        "4844":    ("CMD HD", StorageDeviceCMD)
#    }

    labels = {
        "1001":    "CBM 1001",
        "1540":    "CBM 1540",
        "1541":    "CBM 1541",
        "1542":    "CBM 1541-II",
        "1570":    "CBM 1570",
        "1571":    "CBM 1571",
        "1581":    "CBM 1581",
        "2031":    "CBM 2031",
        "8050":    "CBM 8050",
        "8250":    "CBM 8250",
        "LTK":     "Lt. Kernal",
        "2000":    "CMD FD-2000",
        "4000":    "CMD FD-4000",
        "4844":    "CMD HD",
        "RAMLINK": "RAMLink",
    }

#    if "-dos4000" in vicecommandline and vicecommandline["-dos4000"] is not None:
#      # types["2000"] = "CMD FD-2000"
#      types["4000"] = "CMD FD-4000"

    if args.debug is True:
      ttyio.echo("drivetype.100: oldvalue=%r" % (oldvalue))

    default = "N"
    options = "N"
    menu = {}
    char = ord("A")
    for k, v in labels.items():
      label = v
      if k == oldvalue:
        ttyio.echo("{var:engine.currentoptioncolor}[%s] %s{/all}" % (chr(char), label))
        default = chr(char)
      else:
        ttyio.echo("[%s] %s" % (chr(char), label))

      options += chr(char)

      menu[chr(char)] = k

      char += 1

    if default == "N":
      ttyio.echo("{var:engine.currentoptioncolor}[N] None{/all}")
    else:
      ttyio.echo("[N] None")

    dt = ttyio.inputchar("device %d type: " % (devicenumber), options, default)
    # ttyio.echo("menu=%r" % (menu), interpret=False)
    if dt in menu:
        ttyio.echo("%s" % (menu[dt]))
        return menu[dt]
    ttyio.echo("None")
    return "0"

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
        prompt = "{var:promptcolor}use rtc? {var:optioncolor}[Yn]: {var:inputcolor}"
        currentoption = "Y"
      else:
        prompt = "{var:promptcolor}use rtc? {var:optioncolor}[y{var:currentoptioncolor}N{/all}]: {var:inputcolor}"
        currentoption = "N"
      self.usertc = ttyio.inputboolean(prompt, currentoption)

      if self.savertc is True:
        prompt = "{var:promptcolor}save rtc? {var:optioncolor}[Yn]: {var:inputcolor}"
        currentoption = "Y"
      else:
        prompt = "{var:promptcolor}save rtc? {var:optioncolor}[yN]: {var:inputcolor}"
        currentoption = "N"
      self.savertc = ttyio.inputboolean(prompt, currentoption)
      # add device to rtc list
    return
  def save(self):
    result = {}
    pass

class StorageDeviceRAMLink(StorageDevice):
  def __init__(self, args, number, drivetype="RAMLINK", **kw):
    super().__init__(args, number, drivetype)
    self.hasrtc = True
    self.args = args
    self.mode = 1
    self.cart = None
    self.size = 0
    self.enabled = False

  def edit(self):
    enableramlink = ttyio.inputboolean("{var:promptcolor}enable ramlink? {var:optioncolor}[yN]{var:promptcolor}: {var:inputcolor}", "N")
    if enableramlink is False:
      vice["+ramlink"] = None
      for x in ("-ramlink", "-ramlinkmode", "-ramlinkrtcsave", "+ramlinkrtcsave", "-ramlinksize", "-ramlinkimage", "-ramlinkimagerw", "+ramlinkimagerw" ):
        if x in vice:
          del vice[x]
      return

    vice["-ramlink"] = None

    ramlinkmode = vice["-ramlinkmode"] if "-ramlinkmode" in vice else 1
    prompt = "-ramlinkmode ("
    if ramlinkmode == 1:
      prompt += "{var:currentoptioncolor}1: Normal{/all} 0: Direct"
    else:
      prompt += "1: Normal {var:currentoptioncolor}0: Direct{/all}"
    prompt += ") [01]: "
    ramlinkmode = ttyio.inputchar(prompt, "01", str(ramlinkmode))
    if ramlinkmode == "0":
      ttyio.echo("0: Direct")
    else:
      ttyio.echo("1: Normal")
    vice["-ramlinkmode"] = ramlinkmode

    size = ttyio.inputinteger("ramlink size in MiB (0=Disabled): ", 16)
    if size == 0:
      return (True, "disabled")
    self.size = size

    description = []
    vice["-ramlinksize"] = size
    description.append("[size: %s]" % (bbsengine.pluralize(size, "megabyte", "megabytes")))

    if ttyio.inputboolean("allow write to ramlink image? [{var:currentoptioncolor}Y{/all}n]: {var:inputcolor}", "Y") is True:
        vice["-ramlinkimagerw"] = None
        description.append("[write image: Yes]")
        if "+ramlinkimagerw" in vice:
          del vice["+ramlinkimagerw"]
    else:
        vice["+ramlinkimagerw"] = None
        if "-ramlinkimagerw" in vice:
          del vice["-ramlinkimagerw"]
        description.append("[write image: No]")

    vice["-cartramlink"] = bbsengine.inputfilename(self.args, "{var:promptcolor}cart ramlink bin: {var:inputcolor}", os.path.join(self.args.basedir, "ramlink.bin"), verify=bbsengine.verifyFileExistsReadable)

    vice["-ramlinkimage"] = bbsengine.inputfilename(self.args, "{var:promptcolor}ramlink image: {var:inputcolor}", os.path.join(self.args.basedir, "ramlink.img"), verify=bbsengine.verifyFileExistsReadableWritable)

    ramlinkrtcsave = True if "-ramlinkrtcsave" in vice else False

    prompt = "ramlink rtc save? ["
    if ramlinkrtcsave is True:
      prompt += "{var:currentoptioncolor}Y{/all}n"
    else:
      prompt += "y{var:currentoptioncolor}N{/all}"
    prompt += "]: {var:inputcolor}"
    if ramlinkrtcsave is True:
      default = "Y"
    else:
      default = "N"
    if ttyio.inputboolean(prompt, default) is True:
      vice["-ramlinkrtcsave"] = None
      if "+ramlinkrtcsave" in vice:
        del vice["+ramlinkrtcsave"]
      description.append("[rtc save: Yes]")
    else:
      vice["+ramlinkrtcsave"] = None
      if "-ramlinkcrtsave" in vice:
        del vice["-ramlinkrtcsave"]
      description.append("[rtc save: No]")

    self.enabled = True

    return (True, description)

  add = edit

  def __str__(self):
    if self.enabled is True:
      return "#%2d RAMLINK %dMB" % (self.number, self.size)
    return "#%2d RAMLINK (disabled)" % (self.number)

class StorageDeviceLTK(StorageDevice):
  def __init__(self, args, number, drivetype="LTK", **kw):
    super().__init__(args, number, drivetype, **kw)
    self.type = drivetype
    self.hasrtc = False
    self.fallbacktype = None
    self.args = args
#    print("self.args=%r" % (self.args))
  def build(self):
    vice["-cartcrt"] = self.cartcrt
    vice["-ltkimage0"] = self.ltkimage0
    vice["-ltkimage1"] = self.ltkimage1
    vice["-ltkimage2"] = self.ltkimage2
    vice["-ltkport"] = self.ltkport
    return

  def json(self):
    res = super().json()
    res.update({ "cartcrt": self.cartcrt, "ltkimage0": self.ltkimage0, "ltkimage1": self.ltkimage1, "ltkimage2": self.ltkimage2, "fallbacktype": self.fallbacktype })
    return res

  def edit(self):
      cartcrt = vice["-cartcrt"] if "-cartcrt" in vice else os.path.join(self.args.basedir, "ltk.crt")
      self.cartcrt = bbsengine.inputfilename(self.args, "-cartcrt: ", cartcrt, verify=bbsengine.verifyFileExistsReadable)

      ltkimage0 = vice["-ltkimage0"] if "-ltkimage0" in vice else os.path.join(self.args.basedir, "drive8-0.dlk")
      ltkimage1 = vice["-ltkimage1"] if "-ltkimage1" in vice else os.path.join(self.args.basedir, "drive8-1.dlk")
      ltkimage2 = vice["-ltkimage2"] if "-ltkimage2" in vice else os.path.join(self.args.basedir, "drive8-2.dlk")
      self.ltkimage0 = bbsengine.inputfilename(self.args, "-ltkimage0: ", ltkimage0, verify=bbsengine.verifyFileExistsReadableWritable)
      self.ltkimage1 = bbsengine.inputfilename(self.args, "-ltkimage1: ", ltkimage1, verify=bbsengine.verifyFileExistsReadableWritable)
      self.ltkimage2 = bbsengine.inputfilename(self.args, "-ltkimage2: ", ltkimage2, verify=bbsengine.verifyFileExistsReadableWritable)

      ltkport = vice["-ltkport"] if "-ltkport" in vice else 0
      self.ltkport = ttyio.inputinteger("Set LTK port number (0..15): ", ltkport, verify=verifyLTKPortInRange)
      vice["-ltkport"] = self.ltkport

      ltkio = vice["-ltkio"] if "-ltkio" in vice else 1
      prompt = "{var:promptcolor}Set LTK IO page ("
      if ltkio == "0":
        prompt += "{var:currentoptioncolor}0: 0xDE00{/all}, 1: 0xDF00"
      elif ltkio == "1":
        prompt += "0: 0xDE00, {var:currentoptioncolor}1: 0xDF00{/all}"
      prompt += "): {var:inputcolor}"
      ch = vice["-ltkio"] = ttyio.inputchar(prompt, "01", "1")
      if args.debug is True:
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
      vice["-ltkio"] = int(ch)

      if self.number > 11:
        ttyio.echo("fallback device disabled, #% d is greater than 11." % (self.number))
        return

      if ttyio.inputboolean("{var:promptcolor}use ltk fallback device? {var:optioncolor}[yN]{var:promptcolor}: {var:inputcolor}", "N") is True:
        self.fallbacktype = ttyio.inputstring("fallback device (cbm only): ", "1581")
        vice["-drive%dtype" % (self.number)] = self.fallbacktype
        d = vice[f"-{self.number}"] if f"-{self.number}" in vice else ""
        image = bbsengine.inputfilename(self.args, "{var:promptcolor}fallback image name: {var:inputcolor}", d)
        if image is not None:
          vice[f"-{self.number}"] = image
#          ttyio.echo("-%d set" % (self.number))

      vice["-ltkimage0"] = ltkimage0
      vice["-ltkimage1"] = ltkimage1
      vice["-ltkimage2"] = ltkimage2

      ttyio.echo("setting -kernal to 'kernal'")
      vice["-kernal"] = "kernal"
      return

  add = edit

  def __str__(self):
    buf = "#% d %s" % (self.number, self.type)
#    if self.cartcrt is not None:
#      buf += " cart: %s" % (self.cartcrt)
    if self.fallbacktype is not None:
      buf += f" fallback: {self.fallbacktype}"
    if "-ltkio" in vice:
      ltkio = vice["-ltkio"]
      if ltkio == 0:
        buf += " io: 0xDE00"
      elif ltkio == 1:
        buf += " io: 0xDF00"
      else:
        buf += " io: ERROR"
    if self.ltkport is not None:
      buf += f" port: {self.ltkport}"

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
    self.image = bbsengine.inputfilename(self.args, "{var:promptcolor}image name: {var:inputcolor}", self.image)

  def edit(self):
    for k, v in cbmtypes.items():
      ttyio.echo("[%s] %s" % (k, v))
    t = ttyio.inputstring("type: ", self.type)
    if t not in cbmtypes:
      ttyio.echo("invalid drive type")
      return
    ttyio.echo("selected %s" % (cbmtypes[t]))
    self.type = t

    self.image = bbsengine.inputfilename(self.args, "{var:promptcolor}image name: {var:inputcolor}", self.image)

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
      if ttyio.inputboolean("{var:promptcolor}use rtc? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y") is True:
        self.usertc = True
        if ttyio.inputboolean("{var:promptcolor}save rtc? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y") is True:
          self.savertc = True
    self.image = bbsengine.inputfilename(self.args, "{var:promptcolor}image filename: {var:inputcolor}", self.image)
    self.bin = bbsengine.inputfilename(self.args, "{var:promptcolor}bin filename: {var:inputcolor}", self.bin)
    vice[f"-{self.number}"] = self.image
    vice[f"-drive{self.number}type"] = self.type

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
    number = ttyio.inputinteger("{var:promptcolor}device number: {var:inputcolor}")
    ttyio.echo("{/all}")
    dt = drivetype(args, number)

    subclass = self.subclasses[dt]
    sd = subclass(args, number, dt)
    sd.add()
    ttyio.echo(str(sd), level="debug")
    if self.find(number) is not None:
      ttyio.echo("#%d has already been defined." % (number))
      return False
    if ttyio.inputboolean("{var:promptcolor}add this device? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y") is True:
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
      ttyio.echo(f"device #{number} is not defined", level="error")
      return False
    d.edit(args)
    return True

  def kill(self, args, **kwargs):
    ttyio.echo("kill")
    if len(storagedevices) == 0:
      ttyio.echo("no storage devices defined.", level="error")
      return False
    device = ttyio.inputinteger("{var:promptcolor}kill which device?: {var:inputcolor}")
    if self.find(device) is None:
      ttyio.echo(f"unable to kill #{device} as it has not been defined")
    if device is None or device == 0:
      ttyio.echo("no storage device number entered.")
      return False
    ttyio.echo("no devices killed (not yet implemented)", level='warn")
    return False
