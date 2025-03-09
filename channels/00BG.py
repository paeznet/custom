# -*- coding: utf-8 -*-
#------------------------------------------------------------

from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from core import filetools

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
    path = filetools.translatePath("special://xbmc")
    itemlist.append(Item(channel=item.channel, title="[COLOR yellow]%s[/COLOR]" %path))
    data = httptools.downloadpage(item.url, forced_proxy=forced_proxy_opt).data
    url= scrapertools.find_single_match(data, "<li><a href='([^']+)' role='menuitem'>Codigo Kodi<")
    data = httptools.downloadpage(url, forced_proxy="ProxyWeb:hide.me").data
    url = scrapertools.find_single_match(data, '<a href="(http://bg-tv.xyz[^"]+)"')
    data = httptools.downloadpage(url).data
    code = scrapertools.find_single_match(data, "<h1>([^<]+)<h1>")
    itemlist.append(Item(channel=item.channel, title="Codigo semanal BlackGhost:   [COLOR yellow]%s[/COLOR]" %code))
    return itemlist

