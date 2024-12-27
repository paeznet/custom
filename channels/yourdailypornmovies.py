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
from modules import autoplay

list_quality = []
list_servers = ['mangovideo']

canonical = {
             'channel': 'yourdailypornmovies', 
             'host': config.get_setting("current_host", 'yourdailypornmovies', default=''), 
             'host_alt': ["https://yourdailypornmovies.ws/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

                                # NETU

def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?s=%s" % (host,texto)
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
    soup = create_soup(item.url).find('ul', class_='scrolling generos')
    matches = soup.find_all('li')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text.strip()
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
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
    matches = soup.find_all('div', class_='movie')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        plot = ""
        # action = "play"
        # if logger.info() == False:
            # action = "findvideos"
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('span', class_='current')
    if next_page:
        next_page = soup.find('span', class_='current').find_next_sibling('a')['href']
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist

# https://yourdailypornmovies.ws/africa-bombassa/
# <div id="play-1" class="player-content">
# <iframe width="640" height="480" src="about:blank" data-rocket-lazyload="fitvidscompatible" data-lazy-src="//xpornium.net/embed/7r16jzrkh0m1n9" scrolling="no" frameborder="0" allowfullscreen="true"></iframe>
# https://xpornium.net/embed/7r16jzrkh0m1n9


def findvideos(item):
    logger.info(item)
    itemlist = []
    videos = []
    soup = create_soup(item.url)
    pornstars = soup.find('div', id='dato-1').find_all('a', href=re.compile("/actor/[A-z0-9-]+/"))
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    # if not "/xxxmovies/" in item.url:
        # lista = item.contentTitle.split()
        # lista.insert (0, pornstar)
        # item.contentTitle = ' '.join(lista)
    plot = pornstar
    matches = soup.find('div', class_='player-content').find_all('iframe')
    for elem in matches:
        if elem.get("data-lazy-src", ""):
            url = elem['data-lazy-src']
        else:
            url = elem['src']
        if not "yandexcdn" in url and not "upvideo" in url and not url in videos:
            videos.insert(0, url)
            itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, plot=plot, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist
