def checktcpser(args, filename="tcpser"): # filename="/home/jam/tmp/tcpser-1.1.4/tcpser"):
  bbsengine.setarea("tcpser")
  bbsengine.title("tcpser: check")

  res = subprocess.run([filename, "-V"], capture_output=True, text=True)

  TCPSERVERSTRING = "(TCPSER) 1.1.5_alpha"

  # look for "invalid option -- 'V'" -- (-V added in 1.1.4, older versions will complain of invalid option)
  # ttyio.echo("%r" % (res.stderr))
  # ttyio.echo("stdout=%r" % (res.stdout))
  if res.stdout.find("invalid option -- 'V'") > -1 or res.stderr.find("invalid option -- 'V'") > -1:
    ttyio.echo("The version of tcpser installed is not compatible with imagebbs (>=1.1.4).")
    return False

  if res.stdout.find(TCPSERVERSTRING) > -1 or res.stderr.find(TCPSERVERSIONSTRING) > -1:
    ttyio.echo("The version of tcpser installed should be compatible with imagebbs")
    return True
