import ttyio4 as ttyio

menu = [
    { "label": "clocks", "callback": "clock" },
    { "label": "storage", "callback": "storage" },
    { "label": "modem", "callback": "modem" }
]

ttyio.echo(repr(menu), interpret=False)

def handlemenu(menuitems:list, prompt:str, title:str=None):
  terminalwidth = ttyio.getterminalwidth()
  # ttyio.echo("terminalwidth=%r" % (terminalwidth), level="debug")

  maxlen = 0
  for m in menu:
        l = len(m["label"])
        if l > maxlen:
            maxlen = l

  firstline = False
  ttyio.echo(" {black}{bggray}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)
  if title is None:
    ttyio.echo(" {black}{bggray} {bgwhite}{acs:ulcorner}{acs:hline:%d}{acs:urcorner}{bggray}  {/all}" % (terminalwidth - 7))
  else:
    ttyio.echo(" {black}{bggray} {bgwhite}{acs:ulcorner}{acs:hline:%d}{acs:urcorner}{bggray}  {/all}" % (terminalwidth - 7))
    ttyio.echo(" {black}{bggray} {bgwhite}{acs:vline}%s{acs:vline}{bgdarkgray} {bggray} {/all}" % (title.center(terminalwidth-7)))
    ttyio.echo(" {black}{bggray} {bgwhite}{acs:ltee}{acs:hline:%d}{acs:rtee}{bgdarkgray} {bggray} {/all}" % (terminalwidth - 7))
  ch = ord("A")
  options = ""
  for m in menuitems:
      buf = "[%s] %s" % (chr(ch), m["label"])
      if firstline is True:
          ttyio.echo(" {black}{bggray} {bgwhite} %s {bggray}  {/all}" % (buf.ljust(terminalwidth-7)), wordwrap=False)
          firstline = False
      else:
          ttyio.echo(" {black}{bggray} {bgwhite}{acs:vline}{bgwhite}%s {acs:vline}{bgdarkgray} {bggray} {/all}" % (buf.ljust(terminalwidth-8)), wordwrap=False)
      options += chr(ch)
      ch += 1
  ttyio.echo(" {black}{bggray} {bgwhite}{acs:vline}%s {acs:vline}{bgdarkgray} {bggray} {/all}" % (" "*(terminalwidth-8)), wordwrap=False)

  ttyio.echo(" {black}{bggray} {bgwhite}{acs:vline}%s {acs:vline}{bgdarkgray} {bggray} {/all}" % ("[Q] Quit".ljust(terminalwidth-8)), wordwrap=False)
  options += "Q"

  ttyio.echo(" {black}{bggray} {bgwhite}{acs:llcorner}{acs:hline:%d}{acs:lrcorner}{bgdarkgray} {bggray} {/all}" % (terminalwidth-7))

  ttyio.echo(" {white}{bggray}  {bgdarkgray}%s {bggray} {/all}" % (" "*(terminalwidth-6)), wordwrap=False)
  ttyio.echo(" {bggray}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)

handlemenu(menu, "prompt here")
