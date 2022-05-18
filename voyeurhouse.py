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

# https://camcaps.to https://reallifecam.to  https://voyeur-house.to 
canonical = {
             'channel': 'voyeurhouse', 
             'host': config.get_setting("current_host", 'voyeurhouse', default=''), 
             'host_alt': ["https://voyeur-house.to"], 
             'host_black_list': [], 
             'pattern': ['var base_url = "([^"]+)"'], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel = item.channel, title="Nuevos" , action="lista", url=host + "/videos?o=mr"))
    itemlist.append(Item(channel = item.channel, title="Mas vistos" , action="lista", url=host + "/videos?o=mv&t=m"))
    itemlist.append(Item(channel = item.channel, title="Mejor valorado" , action="lista", url=host + "/videos?o=bw&t=m"))
    itemlist.append(Item(channel = item.channel, title="Mas comentado" , action="lista", url=host + "/videos?o=md&t=m"))
    itemlist.append(Item(channel = item.channel, title="Mas largo" , action="lista", url=host + "/videos?o=lg&t=m"))
    itemlist.append(Item(channel = item.channel, title="Categorias" , action="categorias", url=host + "/categories"))
    itemlist.append(Item(channel = item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search/videos?search_query=%s" % (host,texto)
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
    matches = soup.find_all('div', class_='col-md-3')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('div', class_='title-truncate').text.strip()
        cantidad = elem.find('span', class_='badge')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel = item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
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
    matches = soup.find_all('div', class_='col-sm-6')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['title']
        thumbnail = elem.img['src']
        time = elem.find('div', class_='duration').text.strip()
        quality = elem.find('div', class_='hd-text-icon')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel = item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='prevnext')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel = item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    url = create_soup(item.url).find('div', class_='video-embedded').iframe['src']
    itemlist.append(Item(channel = item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    url = create_soup(item.url).find('div', class_='video-embedded').iframe['src']
    itemlist.append(Item(channel = item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist