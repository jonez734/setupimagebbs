def checkvice(args, **kwargs):
  bbsengine.setarea("checkvice")
  bbsengine.title("check vice features")

  ttyio.echo("checkvice: ", end="", flush=True)
  features = getvicefeatures(args)
  ttyio.echo("OK")
  if "IPV6" in features and features["IPV6"] is True:
    ttyio.echo("IPV6 is enabled.")
  else:
    ttyio.echo("IPV6 is not enabled.")

  if "RS232NET" in features and features["RS232NET"] is True:
    ttyio.echo("RS232NET is enabled.", level="success")
    return True
  else:
    ttyio.echo("RS232NET is not enabled.", level="error")
    return False
