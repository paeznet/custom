# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger, platformtools
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup

canonical = {
             'channel': 'xnostars', 
             'host': config.get_setting("current_host", 'xnostars', default=''), 
             'host_alt': ["https://xnostars.com/"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "videos/p1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "videos/p1-nota"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="catalogo", url=host + "actrices-porno/p1-nota"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categorias/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%sbuscar/%s" % (host,texto)
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
    matches = soup.find('section', class_='videos').find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-src']
        cantidad = elem.find('span', class_='label')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
        itemlist.sort(key=lambda x: x.title)
    return itemlist



def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('section', class_='fotos').find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-src']
        cantidad = elem.find('span', class_='label')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='siguiente')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
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
    matches = soup.find('section', class_='videos').find_all('article')
    if "/buscar/" in item.url:
        matches = soup.find('section', class_='fotos').find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.h3.text.strip()
        thumbnail = elem.img['src'] if elem.img.get('src', '') else ''
        thumbnail = elem.img['data-src'] if elem.img.get('data-src', '') else ''
        time = elem.find('span', class_='duration').text.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        if not "promo" in time:
            itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                                 fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
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

