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
from datetime import datetime, date, timedelta

# https://www.dtp4all.ml  https://www.x4all.ga        https://www.xlatino.ml
canonical = {
             'channel': 'dtp4all', 
             'host': config.get_setting("current_host", 'dtp4all', default=''), 
             'host_alt': ["https://www.dtp4all.ml"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


formato = "%Y-%m-%d"
fecha = date.today().strftime(formato)
logger.debug(fecha)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/search?updated-max=" + fecha + "T03:30:00-08:00&max-results=9", fecha=fecha ))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%s/search?q=%s&max-results=50" % (host,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


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
    soup = create_soup(item.url).find('div', class_='main section')
    matches = soup.find_all('a', class_='post-image-link')
    for elem in matches:
        url = elem['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='blog-pager-older-link')
    if next_page:
        # match = re.search(r'\d{4}-\d{2}-\d{2}', item.url)
        # date = datetime.strptime(match.group(), '%Y-%m-%d').date()
        logger.debug(item.fecha)
        logger.debug(datetime.strptime(item.fecha, '%Y-%m-%d'))
        date = datetime.strptime(item.fecha, '%Y-%m-%d').date()
        next_page = date - timedelta(days=3)
        item.fecha = next_page
        next_page = re.sub(r"updated-max=\d{4}-\d{2}-\d{2}", "updated-max={0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('div', class_='post-body post-content')
    url = soup.iframe['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('div', class_='post-body post-content')
    url = soup.iframe['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

