# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup


canonical = {
             'channel': 'beemtube', 
             'host': config.get_setting("current_host", 'beemtube', default=''), 
             'host_alt': ["https://beemtube.com/"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host + "most-recent/page1.html"))
    itemlist.append(item.clone(title="Mas vistos" , action="lista", url=host + "most-viewed/month/page1.html"))
    itemlist.append(item.clone(title="Mejor valorado" , action="lista", url=host + "top-rated/month/page1.html"))
    itemlist.append(item.clone(title="Mas comentado" , action="lista", url=host + "most-discussed/page1.html"))
    itemlist.append(item.clone(title="Mas largo" , action="lista", url=host + "duration/page1.html"))
    itemlist.append(item.clone(title="PornStar" , action="categorias", url=host + "pornstars/most-popular/page1.html"))
    itemlist.append(item.clone(title="Canal" , action="catalogo", url=host + "channels/"))

    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "categories/?sort_by=avg_videos_popularity&from=01"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch?q=%s&sortby=newest" % (host,texto)
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
    matches = soup.find_all('div', class_='item')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        if ".svg" in thumbnail:
            thumbnail = elem.img['data-src']
        plot = ""
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', string='Next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='channel_item')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        if ".svg" in thumbnail:
            thumbnail = elem.img['data-src']
        cantidad = elem.find('div', class_='channel_item_videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip().replace(" Videos", ""))
        plot = ""
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
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
    matches = soup.find_all('div', class_='content wide')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        if "base64" in thumbnail:
            thumbnail = elem.img['data-src']
        time = elem.find('div', class_='duration').text.strip()
        quality = elem.find('span', class_='hd_video')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(item.clone(action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', string='Next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    url = scrapertools.find_single_match(data, '"playlist": "([^"]+)"')
    data = httptools.downloadpage(url).data
    patron = '"file":"([^"]+)","label":"(\d+p)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if matches:
        for url,quality in matches:
            url = url.replace("\\/", "/")
            itemlist.append(['%s' %quality, url])
        itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    else:
        url = scrapertools.find_single_match(data, '"file":"([^"]+)"')
        url = url.replace("\\/", "/")
        itemlist.append(['mp4', url])
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    url = scrapertools.find_single_match(data, '"playlist": "([^"]+)"')
    data = httptools.downloadpage(url).data
    patron = '"file":"([^"]+)","label":"(\d+p)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if matches:
        for url,quality in matches:
            url = url.replace("\\/", "/")
            itemlist.append(['%s' %quality, url])
        itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    else:
        url = scrapertools.find_single_match(data, '"file":"([^"]+)"')
        url = url.replace("\\/", "/")
        itemlist.append(['mp4', url])
    return itemlist
