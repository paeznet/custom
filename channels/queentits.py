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

#  https://es.chaturbate.com       https://www.queentits.com       https://www.sluts.xyz/
canonical = {
             'channel': 'queentits', 
             'host': config.get_setting("current_host", 'queentits', default=''), 
             'host_alt': ["https://www.queentits.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel = item.channel, title="Mujeres" , action="lista", url=host + "female-cams/"))
    itemlist.append(Item(channel = item.channel, title="Hombres" , action="lista", url=host + "male-cams/"))
    itemlist.append(Item(channel = item.channel, title="Parejas" , action="lista", url=host + "couple-cams/"))
    itemlist.append(Item(channel = item.channel, title="Trans" , action="lista", url=host + "trans-cams/"))
    itemlist.append(Item(channel = item.channel, title="Categorias" , action="submenu"))
    return itemlist

def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel = item.channel, title="Mujeres" , action="categorias", url=host + "tags/f/"))
    itemlist.append(Item(channel = item.channel, title="Hombres" , action="categorias", url=host + "tags/m/"))
    itemlist.append(Item(channel = item.channel, title="Parejas" , action="categorias", url=host + "tags/c/"))
    itemlist.append(Item(channel = item.channel, title="Trans" , action="categorias", url=host + "tags/s/"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ssearch/%s/" % (host,texto)
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
    matches = soup.find_all('div', class_='tag_row')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        cantidad = elem.find('span', class_='rooms')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='item-pagin is_last')
    if next_page:
        next_page = next_page.a['data-parameters'].replace(":", "=").split(";").replace("+from_albums", "")
        next_page = "?%s&%s" % (next_page[0], next_page[1])
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    matches = soup.find_all('li', class_='room_list_room')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['data-room']
        thumbnail = elem.img['src']
        age = elem.find('span', class_='age').text.strip()
        if age:
            title = "%s (%s)" % (title,age)
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = data.replace("\\u0022" , '"').replace("\\u002D", "-")
    url = scrapertools.find_single_match(data, '"hls_source"\: "([^"]+)"')
    itemlist.append(Item(channel = item.channel, action="play", url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = data.replace("\\u0022" , '"').replace("\\u002D", "-")
    url = scrapertools.find_single_match(data, '"hls_source"\: "([^"]+)"')
    itemlist.append(Item(channel = item.channel, action="play", url=url, contentTitle=item.contentTitle))
    return itemlist