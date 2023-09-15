def clock(args, **kwargs):
  bbsengine.setarea("vice: clock")
  bbsengine.title("clock")
# clock1 = ds12c887rtc(args)
#  clock1 =  ttyio.inputboolean("use ds12c887rtc? [{bggray}{white}Y{/all}n]: ", "Y", "YN")
#  if clock1 is False:
  clock2 = ttyio.inputboolean("use cmd fd-4000 RTC? [y{var:engine.currentoptioncolor}N{/all}]: ", "N", "YN")
#  else:
#    clock2 = ttyio.inputboolean("use cmd fd-4000 RTC? [{bggray}{white}Y{/all}n]: ", "Y", "YN")

#  if clock1 is True and clock2 is True:
#    if ttyio.inputboolean("do you really want to use both the cmd rtc and ds12c887rtc? [yN]: ", "N", "YN") is False:
#      ttyio.echo("aborted", level="error")
#      return False

  status = []
  if clock2 is True:
    cmd4000(args)
    status.append("cmd fd-4000rtc")
  if len(status) > 0:
    statusbuf = "(%s)" % (ttyio.readablelist(status))
  else:
    statusbuf = ""

  return (True, (status,)) # statusbuf)
