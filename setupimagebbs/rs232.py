def rs232(args, **kwargs):
  bbsengine.setarea("vice: rs232/ip232")
  bbsengine.title("vice: rs232/ip232")
  dev = ttyio.inputinteger("device [1-{var:engine.currentoptioncolor}4{/all}]: ", 4)
  vicecommandline["+rsuser"] = None
  vicecommandline["-rsdev%d" % (dev)] = "%s:%s" % (localhost, tcpsercommandline["-v"])
  ip232 = ttyio.inputboolean("enable ip232? [{var:engine.currentoptioncolor}Y{/all}n]: ", "Y")
  vicecommandline["-rsdev%dip232" % (dev)] = ip232
  baud = ttyio.inputinteger("baud rate: ", tcpsercommandline["-s"]) # 38400
  vicecommandline["-rsdev%dbaud" % (dev)] = baud

  resultbuf = "[dev: %d] [ip232: %s] [baud: %d]" % (dev, ip232, baud)

#  ttyio.echo("configured rsdev%d as ip232." % (dev))
  return (True, resultbuf)
