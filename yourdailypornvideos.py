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

host = 'https://yourdailypornvideos.ws'

# SOLO LOS ULTIMOS BUSCADOR FALLA servers obsoletos

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host))
    # itemlist.append(item.clone(title="Top 100" , action="lista", url=host + "/top-100-porn/"))
    itemlist.append(item.clone(title="Catalogo" , action="categorias", url=host))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?s=%s" % (host,texto)
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
    soup = create_soup(item.url)
    matches = soup.find_all('ul', class_='sub-menu')
    for elem in matches:
        sec = elem.find_previous_sibling("a")
        em = elem.find_all('li')
        for elem in em:
            url = elem.a['href']
            title = elem.a.text.strip()
            thumbnail = ""
            plot = ""
            if not "#SITERIPS" in sec.text:
                itemlist.append(item.clone(action="lista", title=title, url=url, thumbnail=thumbnail , plot=plot) )
            # else:
                # if not "SITERIP" in title:
                    # title += " SITERIP"
                # itemlist.append(item.clone(action="findvideos", title=title, url=url, thumbnail=thumbnail , plot=plot) )
                
    return itemlist

def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='thumb-wrap')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        if not "yourdailypornvideos.ws" in thumbnail:
            thumbnail = elem.img['data-lazy-src']
        thumbnail = thumbnail.replace("120x76", "326x235")
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(item.clone(action="findvideos", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('span', class_='current')
    if next_page:
        next_page = soup.find('span', class_='current').find_next_sibling('a')['href']
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info(item)
    itemlist = []
    soup = create_soup(item.url).find('article')
    matches = soup.find_all('iframe')
    for elem in matches:
        url = elem['src']
        if not "yandexcdn" in url and not "upvideo" in url:
            itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

