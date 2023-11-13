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
