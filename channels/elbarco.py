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
from bs4 import BeautifulSoup

#   https://telegra.ph/AGENDA-DEPORTIVA-2504-04-25
    # acestream://9dad717d99b29a05672166258a77c25b57713dd5


# https://porlacaraveoelfutbol.pages.dev/   https://www.futbolenlatv.es/
# https://tvglobalrpi.blogspot.com/p/canales-acestream-actualizados.html?m=1

# https://acestreamsearch.net/en/?q=el


canonical = {
             'channel': 'elbarco', 
             'host': config.get_setting("current_host", 'elbarco', default=''), 
             'host_alt': ["https://telegra.ph/"], 
             'host_black_list': [], 
             # 'pattern': ['href="?([^"|\s*]+)["|\s*]\s*rel="?stylesheet"?'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]



def mainlist(item):
    logger.info()
    itemlist = []
    
    url = "%sAGENDA-DEPORTIVA-2504-04-25" % host
    
    soup = create_soup(url).find('article')
    matches = soup.find_all('strong')[:-2]
    lista = []
    n=0
    
    for x , value in enumerate(matches):
        if value.text.strip().isupper():
            lista.append(x)
            id = x
            n+= 1
            corta=[]
        if len(lista) == n:
            corta.append(value.text.strip())
            lista[n-1] = corta
    
    for elem in lista:
        itemlist.append(Item(channel=item.channel, title="[COLOR blue]%s[/COLOR]" % elem[0]))
        for x , value in enumerate(elem):
            if x % 2 == 0 and not x == 0:
                url = "plugin://script.module.horus?action=play&id=%s&title=%s" % (value, elem[x-1])
                title = ".......%s" % elem[x-1]
                # logger.debug(url + title)
                itemlist.append(Item(channel=item.channel, action="play", title=title, url=url))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ssearch/%s/?sort_by=post_date&from_videos=01" % (host,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
    return []


def categorias(item):
    logger.info()
    itemlist = []
    
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
