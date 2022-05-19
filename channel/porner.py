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

host = 'https://porner.tv'


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/hottest-videos/page/1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/most-viewed-videos/page/1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/most-liked-videos/page/1"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/pornstars/page/1"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/channels/page/1"))

    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%s/search?q=%s" % (host,texto)
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
    matches = soup.find_all('a', class_=re.compile(r"^Single\w+List"))
    for elem in matches:
        logger.debug(elem)
        url = elem['href']
        title = elem.img['alt']
        thumbnail = elem.img['data-src']
        url = urlparse.urljoin(host,url)
        url += "/page/1"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='page-item active')
    page = scrapertools.find_single_match(item.url, "(.*?/page/)")
    if next_page:
        next_page = next_page.find_next_sibling('li')
        next_page = "%s%s" % (page, next_page.text)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    matches = soup.find_all('a', class_='SingleVideoItemLink')
    for elem in matches:
        url = elem['href']
        title = elem.img['alt']
        thumbnail = elem.img['data-src']
        time = elem.find('span', class_='Duration')
        quality = elem.find('span', class_='Hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time.text.strip(),title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time.text.strip(),title)
        url = urlparse.urljoin(host,url)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('li', class_='page-item active')
    page = scrapertools.find_single_match(item.url, "(.*?/page/)")
    if next_page:
        next_page = next_page.find_next_sibling('li')
        next_page = "%s%s" % (page, next_page.text)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    id = scrapertools.find_single_match(data, '"videoID":(\d+),')
    rd = int(id)/1000*1000
    if rd == 0:
        rd = "00000"
    url = "https://pornercdns.com/hls/00%s/%s/master.m3u8" %(rd,id)
    itemlist.append(Item(channel=item.channel, action="play", title= url, contentTitle = item.contentTitle, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data, '"file":"([^"]+)"')
    url = url.replace("\/", "/")
    itemlist.append(Item(channel=item.channel, action="play", title= url, contentTitle = item.contentTitle, url=url))
    # itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
