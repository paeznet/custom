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

from platformcode import config, logger, platformtools
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup

canonical = {
             'channel': 'xnostars', 
             'host': config.get_setting("current_host", 'xnostars', default=''), 
             'host_alt': ["https://xnostars.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/videos/p1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/videos/p1-nota"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="catalogo", url=host + "/actrices-porno/p1-nota"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categorias/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/buscar/?q=%s&Tipo=videos&sa=Buscar" % (host,texto)
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
    matches = soup.find('div', class_='menu-actrices').find_all('li')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text.strip()
        thumbnail = ""
        url = urlparse.urljoin(item.url,url)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    return itemlist



def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('section', class_='list-actrices').find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.h1.text.strip()
        thumbnail = elem.img['data-src']
        cantidad = elem.find('span', class_='label')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', title='página siguiente')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    matches = soup.find('section', class_='videos').find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.h1.text.strip()
        thumbnail = elem.img['data-src']
        time = elem.find('span', class_='duration').text.strip()
        pornstar = elem.img['alt']
        pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
        title = "[COLOR yellow]%s[/COLOR] %s %s" % (time,pornstar,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        if not "promo" in time:
            itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                                   plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', title='página siguiente')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('div', class_='wrapper-video').iframe['src']
    if not url.startswith("https"):
        url = "https:%s" % url
    if "xh.video" in url:
        url = httptools.downloadpage(url).url
    elif "videomega." in url:
        url= ""
    if url:
        itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
        itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('div', class_='wrapper-video').iframe['src']
    if not url.startswith("https"):
        url = "https:%s" % url
    if "xh.video" in url:
        url = httptools.downloadpage(url).url
    elif "videomega." in url:
        url= ""
    if url:
        itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
        itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    else:
        platformtools.dialog_ok("videomega: Error", "El archivo no existe o ha sido borrado")
        return
    return itemlist

