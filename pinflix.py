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
             'channel': 'pinflix', 
             'host': config.get_setting("current_host", 'pinflix', default=''), 
             'host_alt': ["https://www.pinflix.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/?order=newest&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/?order=most-popular&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/?order=top-rated&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "/?order=longest&page=1"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/pornstars?page=1"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/channel?page=1"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/category"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search?search=%s&page=1" % (host,texto)
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
    soup = create_soup(item.url) #.find('section', class_='columns')
    matches = soup.find_all('a', class_='column')
    for elem in matches:
        url = elem['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-src']
        cantidad = elem.find('div', class_='is-size-7')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='pagination-next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
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
    matches = soup.find_all('div', class_='is-half-tablet')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-src']
        time = elem.find('span', class_='video-duration').text.strip()
        quality = elem.find('span', class_='label hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='lazy-paginator-btn')
    if next_page:
        next_page = next_page['data-next-page']
        next_page = re.sub(r"&page=\d+", "&page={0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('video')
    matches = soup.find_all('source')
    for elem in matches:
        url = elem['src']
        url = httptools.downloadpage(url, follow_redirects=False).headers["location"]
        quality = elem['label']
        itemlist.append(Item(channel=item.channel, action="play", title= "mp4", contentTitle = item.title, url=item.url))
    return itemlist[::-1]


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('video')
    matches = soup.find_all('source')
    for elem in matches:
        url = elem['src']
        url = httptools.downloadpage(url, follow_redirects=False).headers["location"]
        quality = elem['label']
        itemlist.append(['.mp4 %s' %quality, url])
    return itemlist[::-1]
