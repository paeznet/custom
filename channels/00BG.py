# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host= "http://www.blackghost.online/"
forced_proxy_opt = 'ProxyWeb:hide.me'

# http://bg-tv.xyz/code/?code=YmxhY2thZGRvbg

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="CODIGO" , action="lista", url=host))
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, forced_proxy=forced_proxy_opt).data
    url= scrapertools.find_single_match(data, "<li><a href='([^']+)' role='menuitem'>Codigo Kodi<")
    data = httptools.downloadpage(url, forced_proxy="ProxyWeb:hide.me").data
    url = scrapertools.find_single_match(data, '<a href="(http://bg-tv.xyz[^"]+)"')
    data = httptools.downloadpage(url).data
    code = scrapertools.find_single_match(data, "<h1>([^<]+)<h1>")
    itemlist.append(Item(channel=item.channel, title="Codigo semanal BlackGhost:   [COLOR yellow]%s[/COLOR]" %code))
    return itemlist

