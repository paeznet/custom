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
             'channel': 'vaginaNL', 
             'host': config.get_setting("current_host", 'vaginaNL', default=''), 
             'host_alt': ["https://en.vagina.nl"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/sexfilms/newest"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/sexfilms/views?period=month"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/sexfilms/top"))
    itemlist.append(Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "/sexfilms/popular?period=month"))
    itemlist.append(Item(channel=item.channel, title="Mas longitud" , action="lista", url=host + "/sexfilms/longest"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/pornstars"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/labels"))

    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%s/sexfilms/search?q=%s&order=published" % (host,texto)
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
    matches = soup.find_all('div', class_='list-item')
    for elem in matches:
        bor = elem.find('a', class_='thumbnail-link')
        url = bor['href']
        title = bor.img['alt']
        thumbnail = bor.img['src']
        if "gif" in thumbnail:
            thumbnail = bor.img['data-src']
        cantidad = elem.find('span', class_='pill')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    if "categories" in item.url:
        itemlist.sort(key=lambda x: x.title)
    next_page = soup.find('span', class_='next')
    if next_page and next_page.find_next_sibling("a"):
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url).data
        data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_='list-rows').find_all('div', class_='list-item')
    for elem in matches:
        if not elem.find('script'):
            url = elem.a['href']
            title = elem.img['alt']
            thumbnail = elem.img['data-src']
            time = elem.find('div', class_='timecode').text.strip()
            quality = elem.find('span', class_='label hd')
            if time:
                title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
            if quality:
                title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
            url = urlparse.urljoin(item.url,url)
            plot = ""
            action = "play"
            if logger.info() == False:
                action = "findvideos"
            itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                                   plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('span', class_='next')
    if next_page and next_page.find_next_sibling("a"):
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('video').source['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist



def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('video').source['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
