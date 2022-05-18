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
             'channel': 'justporn', 
             'host': config.get_setting("current_host", 'justporn', default=''), 
             'host_alt': ["https://justporn.com"], 
             'host_black_list': [], 
             'pattern': ['hreflang="?x-default"?\s*href="?([^"|\s*]+)["|\s*]'], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

# https://justporn.com/ajax/videos.php?lang=en&page=2
# https://justporn.com/ajax/videos.php?lang=en&page=2&sort=top-rated&range=30

def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/?page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/?sort=most-viewed&range=30&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/?sort=top-rated&range=30&page=1"))
    # itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "/most-commented/1/?sort_by=most_commented_month&from=01"))
    # itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/models/?sort_by=avg_videos_popularity&from=01"))
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/sites/?sort_by=avg_videos_popularity&from=01"))

    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    # itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%s/search/%s/" % (host,texto)
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
    matches = soup.find_all('div', class_='featured-category')
    for elem in matches:
        val = elem['data-val']
        title = elem.text.strip()
        url = "/?category[]=%s&page=1"  %val
        thumbnail = ""
        url = urlparse.urljoin(item.url,url)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    itemlist.sort(key=lambda x: x.title)
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
    matches = soup.find_all('div', class_='content')
    for elem in matches:
        pornstar = ""
        quality = ""
        url = elem['data-clip']
        title = elem.h2.text.strip()
        thumbnail = elem.img['src']
        time = elem.find('div', class_='content-img-details').text.strip()
        pornstars = elem.find_all('a', class_='acters')
        for x , value in enumerate(pornstars):
            pornstars[x] = value.text.strip()
        pornstar = ' & '.join(pornstars)
        pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
        time = time.split()
        if len(time) == 2:
            quality = time[-1].upper()
        time = time[0]
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s %s" % (time, quality,pornstar,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s %s" % (time,pornstar,title)
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('div', class_='btn-more')
    if next_page:
        page = scrapertools.find_single_match(item.url, 'page=([0-9]+)')
        next_page = int(page) + 1
        next_page = re.sub(r"page=\d+", "page={0}".format(next_page), item.url)
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
