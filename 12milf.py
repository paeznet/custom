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

##  https://www.12milf.com  https://www.poldertube.nl  https://www.porntube.nl      https://www.sextube.nl
canonical = {
             'channel': '12milf', 
             'host': config.get_setting("current_host", '12milf', default=''), 
             'host_alt': ["https://www.12milf.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel = item.channel, title="Nuevos" , action="lista", url=host + "/?filter=latest"))
    itemlist.append(Item(channel = item.channel, title="Mas vistos" , action="lista", url=host + "/?filter=most-viewed"))
    itemlist.append(Item(channel = item.channel, title="Mejor valorado" , action="lista", url=host + "/?filter=popular"))
    itemlist.append(Item(channel = item.channel, title="Mas metraje" , action="lista", url=host + "/?filter=longest"))
    itemlist.append(Item(channel = item.channel, title="Categorias" , action="categorias", url=host + "/categorieen/"))
    itemlist.append(Item(channel = item.channel, title="Buscar", action="search"))
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
    soup = create_soup(item.url)
    matches = soup.find_all('article', id=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.find('span', class_='cat-title').text.strip()
        thumbnail = elem.img['src']
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
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
    # if isinstance(logger.info(), bool):
    # action = isinstance(logger.info(), bool)
    soup = create_soup(item.url)
    matches = soup.find_all('article', id=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-src']
        time = elem.find('span', class_='duration').text.strip()
        quality = elem.find('span', class_='is-hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel = item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='current')
    if next_page:
        next_page = next_page.find_next('a')['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel = item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).video
    matches = soup.find_all('source')
    for elem in matches:
        url = elem['src']
        quality = elem['label']
        url += "|Referer=%s" % host
        itemlist.append(Item(channel = item.channel, action="play", title=quality, url=url) )
    return itemlist[::-1]


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).video
    matches = soup.find_all('source')
    for elem in matches:
        url = elem['src']
        quality = elem['label']
        url += "|Referer=%s" % host
        itemlist.append(['%s' %quality, url])
    return itemlist[::-1]
