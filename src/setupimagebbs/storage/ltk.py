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
      self.cartcrt = bbsengine.inputfilename(self.args, "-cartcrt: ", cartcrt, verify=bbsengine.util.verifyFileExistsReadable)

      ltkimage0 = vice["-ltkimage0"] if "-ltkimage0" in vice else os.path.join(self.args.basedir, "drive8-0.dlk")
      ltkimage1 = vice["-ltkimage1"] if "-ltkimage1" in vice else os.path.join(self.args.basedir, "drive8-1.dlk")
      ltkimage2 = vice["-ltkimage2"] if "-ltkimage2" in vice else os.path.join(self.args.basedir, "drive8-2.dlk")
      self.ltkimage0 = bbsengine.inputfilename(self.args, "-ltkimage0: ", ltkimage0, verify=bbsengine.util.verifyFileExistsReadableWritable)
      self.ltkimage1 = bbsengine.inputfilename(self.args, "-ltkimage1: ", ltkimage1, verify=bbsengine.util.verifyFileExistsReadableWritable)
      self.ltkimage2 = bbsengine.inputfilename(self.args, "-ltkimage2: ", ltkimage2, verify=bbsengine.util.verifyFileExistsReadableWritable)

      ltkport = vice["-ltkport"] if "-ltkport" in vice else 0
      self.ltkport = ttyio.inputinteger("{var:promptcolor}Set LTK port number (0..15): {var:inputcolor}", ltkport, verify=verifyLTKPortInRange)
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
    buf = f"#{self.number} {self.type}"
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
