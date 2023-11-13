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
    number = ttyio.inputinteger("{var:promptcolor}device number: {var:inputcolor}")
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
