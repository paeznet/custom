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

canonical = {
             'channel': 'pornhits', 
             'host': config.get_setting("current_host", 'pornhits', default=''), 
             'host_alt': ["https://www.pornhits.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "videos.php?p=1&s=l"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "videos.php?p=1&s=pw"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "videos.php?p=1&s=bw"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars.php?p=1&s=avp&mg=f"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "sites.php?p=1&s=avp"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories.php"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
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
    matches = soup.find('div', class_='box').find_all('a', class_='item')
    if "models" in item.url:
        matches.pop(0)
    for elem in matches:
        url = elem['href']
        title = elem['title'].replace("porn videos", "" )
        if "categories" in item.url:
            thumbnail = ""
        else:
            thumbnail = elem.img['src']
        cantidad = elem.find('div', class_='videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    pagination = soup.find('span', class_='pagination2874')
    if pagination:
        page = pagination['data-page']
        total = pagination['data-total']
        next_page = int(page) + 1
        last_page = int(total)/36
        if next_page < last_page:
            next_page = re.sub(r"\d+&s=", "{0}&s=".format(next_page), item.url)
            itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('a', class_='more')
    for elem in matches:
        logger.debug(elem)
        url = elem['href']
        title = elem.parent.h2.text.strip()
        thumbnail = ""
        url = urlparse.urljoin(item.url,url)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    pagination = soup.find('span', class_='pagination2874')
    page = pagination['data-page']
    total = pagination['data-total']
    next_page = int(page) + 1
    last_page = int(total)/36
    if next_page < last_page:
        next_page = re.sub(r"\d+&s=", "{0}&s=".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    matches = soup.find('div', class_='list-videos').find_all('div', class_='item')
    for elem in matches:
        logger.debug(elem)
        url = elem.a['href']
        title = elem.find('strong', class_='title').text.strip()
        title = " ".join(title.split())
        thumbnail = elem.img['data-original']
        time = elem.find('span', class_='duration').text.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    pagination = soup.find('span', class_='pagination2874')
    page = pagination['data-page']
    total = pagination['data-total']
    next_page = int(page) + 1
    last_page = int(total)/36
    if next_page < last_page:
        next_page = re.sub(r"\d+&s=", "{0}&s=".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

def play(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
