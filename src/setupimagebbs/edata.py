import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import lib

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args=None, **kw):
    return None

def main(args, **kwargs):
  data = [
    {"record": 21, "type": "inputchar",           "prompt": "System Reservation Password", "choices": ["0=None", "1=Once", "2=All"], "options": "012", "default": "0", "value":None},
    {"record": 32, "type": "inputchar",           "prompt": "RS232 Device", "choices": ["0=User Port", "1=Swiftlink"], "options": "01", "default": "1", "value":None},
    {"record": 37, "type": "inputrtcdevice",      "prompt": "RTC device number", "value":None},
    {"record": 38, "type": "inputltkdevice",      "prompt": "LTK device number", "default": "8", "value":None},
    {"record": 43, "type": "inputstring",         "prompt": "Password Mask Char", "default": "X", "value":None},
    {"record": 47, "type": "inputstring",         "prompt": "BBS Name", "default": "NEEDINFO", "value":None},
    {"record": 51, "type": "inputbbsid",          "prompt": "BBS Identifier", "default": "NEEDINFO", "value":None},
    {"record": 52, "type": "inputdevicedrive",    "prompt": "System Device, Drive", "default": "8,1", "value":None},
    {"record": 53, "type": "inputdevicedrive",    "prompt": "E-Mail Device, Drive", "default": "8,2", "value":None},
    {"record": 54, "type": "inputdevicedrive",    "prompt": "Etcetera Device, Drive", "default": "8,1", "value":None},
    {"record": 55, "type": "inputdevicedrive",    "prompt": "Directory", "default": "8,0", "value":None},
    {"record": 56, "type": "inputdevicedrive",    "prompt": "Modules", "default": "8,0", "value":None},
    {"record": 57, "type": "inputdevicedrive",    "prompt": "User", "default": "8,1", "value":None},
    {"record": 58, "type": "inputnewusercredits", "prompt": "Credits for new user", "default": "100", "value":None},
  ]
  
  bbsengine.util.heading("set up e.data")
  return True

