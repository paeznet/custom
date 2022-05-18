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
from channels import autoplay

list_quality = ['default']
list_servers = []

# https://playpornfree.org/   https://streamporn.pw/  https://mangoporn.net/   https://watchfreexxx.net/   https://losporn.org/  https://xxxstreams.me/  https://speedporn.net/
# "https://watchfreexxx.net/"  #  pandamovie https://watchpornfree.info  #'https://xxxparodyhd.net'  'http://www.veporns.com'  'http://streamporno.eu'
# https://www.netflixporno.net  https://xxxscenes.net   https://mangoporn.net   https://speedporn.net
canonical = {
             'channel': 'netflixporno', 
             'host': config.get_setting("current_host", 'netflixporno', default=''), 
             'host_alt': ["https://www.netflixporno.net"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s*hreflang="?en"?'], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Peliculas" , action="lista", url=host + "/adult/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/adult/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/adult/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host + "/adult/"))

    itemlist.append(Item(channel=item.channel, title="Videos" , action="submenu", url=host + "/scenes/"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Videos" , action="lista", url=item.url))
    itemlist.append(Item(channel=item.channel, title="Destacados" , action="lista", url=host + "/scenes/category/featured-scenes/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=item.url))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host, vid = "vid"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search/%s" % (item.url,texto)
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
    logger.debug(soup)
    if "Canal" in item.title:
        matches = soup.find_all('li', class_='menu-item-object-director')
    else:
        matches = soup.find_all('li', class_='cat-item')
    for elem in matches:
        url = elem.a['href']
        if item.vid:
            url = url.replace("/adult/", "/scenes/")
        title = elem.a.text.strip()
        thumbnail = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, thumbnail=thumbnail) )
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
    matches = soup.find_all('article', class_='TPost B')
    for elem in matches:
        url = elem.a['href']
        title = elem.find(class_='Title').text.strip()
        thumbnail = elem.img['src']
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    video_urls = []
    soup = create_soup(item.url).find('div', id='pettabs')
    matches = soup.find_all('a')
    for elem in matches:
        url = elem['href']
        url = url.split("?link=")[-1]
        if not url in video_urls:
            video_urls += url
            itemlist.append(item.clone(title='%s', url=url, action='play', language='VO',contentTitle = item.contentTitle))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist

