import argparse
from bbsengine6 import io
import bbsengine6 as bbsengine

from . import lib

def init(args: argparse.Namespace, **kwargs) -> bool | None:
    return True

def access(args: argparse.Namespace, op: str, **kwargs) -> bool | None:
    return True

def buildargs(args: argparse.Namespace, **kwargs) -> argparse.ArgumentParser | None:
    return None

def main(args: argparse.Namespace, **kwargs) -> bool | None:
  vice = kwargs["vice"] if "vice" in kwargs else None

  bbsengine.util.heading("ds12c887rtc")

  if "-ds12c887rtc" in vice:
    ch = io.inputboolean("{var:promptcolor}Enable DS12C887RTC? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y", "YN")
  elif "+ds12c887rtc" in vice:
    ch = io.inputboolean("{var:promptcolor}Enable DS12C887RTC? {var:optioncolor}[yN]{var:promptcolor}: {var:inputcolor}", "N", "YN")
  else:
    ch = io.inputboolean("{var:promptcolor}Enable DS12C887RTC? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y", "YN")

  if ch is False:
    vice["+ds12c887rtc"] = None
    if "-ds12c887rtc" in vice:
      del vice["-ds12c887rtc"]
    return True
  else:
    vice["-ds12c887rtc"] = None
    if "+ds12c887rtc" in vice:
      del vice["+ds12c887rtc"]

  if "-ds12c887rtcsave" in vice:
    ch = io.inputboolean("{var:promptcolor}Enable saving of the DS12C887RTC data when changed? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y", "YN")
  elif "+ds12c887rtcsave" in vice:
    ch = io.inputboolean("{var:promptcolor}Enable saving of the DS12C887RTC data when changed? {var:optioncolor}[yN]{var:promptcolor}: {var:inputcolor}", "N", "YN")
  else:
    ch = io.inputboolean("{var:promptcolor}Enable saving of the DS12C887RTC data when changed? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y", "YN")

  if ch is False:
    vice["+ds12c887rtcsave"] = None
  else:
    vice["-ds12c887rtcsave"] = None

  addresschoices = ["0xD500","0xD600","0xD700", "0xDE00","0xDF00"]

  currentaddr = vice["-ds12c887rtcbase"] if "-ds12c887rtcbase" in vice else None

  defaultvalue = "0xD700"

  menu = []
  ch = ord("A")
  options = ""
  for c in addresschoices:
    i = ch - ord("A")
    if currentaddr == addresschoices[i] or defaultvalue == addresschoices[i]:
      menu.append(f"{{var:engine.currentoptioncolor}}[{chr(ch)}] {addresschoices[i]}")
      defaultvalue = chr(ch)
    elif currentaddr in ioaddrs:
      menu.append("{darkgray}[%s] %s{/all}" % (chr(ch), addresschoices[i]))
    else:
      menu.append("[%s] %s" % (chr(ch), addresschoices[i]))
    options += chr(ch)
    ch += 1

  ch = io.inputchar("ioaddr "+" ".join(menu)+": ", options, defaultvalue, noneok=False)
  addr = addresschoices[ord(ch) - ord("A")]
  io.echo(addr)
  if addr in ioaddrs:
    if io.inputboolean("that address is already used for %s. proceed? [y{var:engine.currentoptioncolor}N{/all}]: " % (ioaddrs[addr]), "N", "YN") is True:
      vice["-ds12c887rtcbase"] = addr
      ioaddrs[addr] = "ds12c887rtc"

  # -ds12c887rtchalted -> Set the RTC oscillator to 'halted'
  # -ds12c887rtcrunning -> Set the RTC oscillator to 'running'
  if "-ds12c887rtcrunning" in vice:
    ch = io.inputchar("{var:promptcolor}Set the RTC oscillator to {var:currentoptioncolor}[R]unning{var:promptcolor} or [H]alted: {var:inputcolor}", "RH", "R")
  elif "-ds12c887rtchalted" in vice:
    ch = io.inputchar("{var:promptcolor}Set the RTC oscillator to [R]unning or {var:engine.currentoptioncolor}[H]alted{var:promptcolor}: {var:inputcolor}", "RH", "H")
  else:
    ch = io.inputchar("Set the RTC oscillator to {var:engine.currentoptioncolor}[R]unning{var:promptcolor} or [H]alted: {var:inputcolor}", "RH", "R")

  if ch == "R":
    io.echo("Running")
    vice["-ds12c887rtcrunning"] = None
    if "-ds12c887rtchalted" in vice:
      del vice["-ds12c887rtchalted"]
  elif ch == "H":
    io.echo("Halted")
    vice["-ds12c887rtchalted"] = None
    if "-ds12c887rtcrunning" in vice:
      del vice["-ds12c887rtcrunning"] 

  if ch is False:
    vice["-ds12c887running"] = None
    if "-ds12c887halted" in vice:
      del vice["-ds12c887halted"]
  else:
    vice["-ds12c887halted"] = None
    if "-ds12c887running" in vice:
      del vice["-ds12c887running"]

  io.echo()
  return True
