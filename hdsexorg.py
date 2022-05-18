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
             'channel': 'hdsexorg', 
             'host': config.get_setting("current_host", 'hdsexorg', default=''), 
             'host_alt': ["https://hdsex.org"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

#                            Forbidden  m3u 
    # https://v028.hdsex.org/d/c/3/dc341fdc185fab24dd839aa358c3a7b0/stream/720p/index.m3u8?h=18e87b2849827a1da693d1f8814a93ba&e=1637076902


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/?sort=-created"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/?sort=-views"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/?"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="catalogo", url=host + "/models?sort=-views"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%s/search/%s" % (host,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_='models').find_all('a')
    for elem in matches:
        url = elem['href']
        thumbnail = elem.img['data-src']
        title = elem.h2.text.strip()
        cantidad = elem.find('div', class_='model__uploaded-videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='pagination__button-next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('a', class_='categories__link-wrapper')
    for elem in matches:
        url = elem['href']
        title = elem['data-title']
        url = urlparse.urljoin(item.url,url)
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
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
    matches = soup.find_all('div', class_='video')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        if elem.img.get("data-src", ""):
            thumbnail = elem.img['data-src']
        else:
            thumbnail = elem.img['src']
        time = elem.find('div', class_='video__info')['data-duration']
        pornstar = elem.find('div', class_='video__models')
        if pornstar:
            pornstar = pornstar.find_all('a')
            for x , value in enumerate(pornstar):
                pornstar[x] = value.text.strip()
            pornstar = ' & '.join(pornstar)
            title = "[COLOR yellow]%s[/COLOR] [COLOR cyan]%s[/COLOR] %s" % (time,pornstar,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='pagination__button-next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('source')['src']
    url = httptools.downloadpage(url, follow_redirects=False).headers["location"]
    # url += "|verifypeer=false"
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('source')['src']
    # url = httptools.downloadpage(url, follow_redirects=False).headers["location"]
    # url += "|verifypeer=false"
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
