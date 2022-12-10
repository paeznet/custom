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

host = ''
canonical = {
             'channel': 'drpornofilme', 
             'host': config.get_setting("current_host", 'drpornofilme', default=''), 
             'host_alt': ["https://www.drpornofilme.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel = item.channel, title="Nuevos" , action="lista", url=host ))
    itemlist.append(Item(channel = item.channel, title="Mejor valorado" , action="lista", url=host + "am-meisten-gestimmt/"))
    itemlist.append(Item(channel = item.channel, title="PornStar" , action="categorias", url=host + "pornostars/"))
    itemlist.append(Item(channel = item.channel, title="Canal" , action="categorias", url=host + "websites/"))

    itemlist.append(Item(channel = item.channel, title="Categorias" , action="categorias", url=host + "kategorien/"))
    itemlist.append(Item(channel = item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssuchen/?q=%s" % (host,texto)
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
    if "pornostar" in item.url:
        matches = soup.find_all('div', class_='wrap-box-chica')
    else:
        matches = soup.find_all('div', class_='wrap-box-escena')
    for elem in matches:
        url = elem.a['href']
        title = elem.h4.text.strip()
        thumbnail = elem.img['data-src']
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel = item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    if "kategorien" in item.url:
        itemlist.sort(key=lambda x: x.title)
    next_page = soup.find('li', class_='pagination_item pagination_item--next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel = item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    soup = create_soup(item.url)
    matches = soup.find('div', class_='grid--videos').find_all('div', class_='box-escena')
    for elem in matches:
        url = elem.a['href']
        title = elem.h4.text.strip()
        thumbnail = elem.img['data-src']
        time = elem.find('div', class_='duracion').text.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel = item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('li', class_='pagination_item pagination_item--next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel = item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s" , contentTitle=item.title, url=item.url)) 
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s" , contentTitle=item.title, url=item.url)) 
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    return itemlist
