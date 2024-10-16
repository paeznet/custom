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
             'channel': 'videosection', 
             'host': config.get_setting("current_host", 'videosection', default=''), 
             'host_alt': ["https://videosection.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/models?sort=-videos_count"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/channels?sort=-videos_count"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host))
    itemlist.append(Item(channel=item.channel, title=""))
    itemlist.append(Item(channel=item.channel, title="Trans", action="submenu", url=host + "/shemales" ))
    itemlist.append(Item(channel=item.channel, title="Gay", action="submenu", url=host + "/gays" ))

    
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=item.url + "/models?sort=-videos_count"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=item.url + "/channels?sort=-videos_count"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=item.url))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%s/search/%s?sort=-created&p=1" % (item.url,texto)
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
    if "channels" in item.url:
        matches = soup.find_all('a', class_='channel')
    elif "models" in item.url:
        matches = soup.find_all('div', class_='model-item')
    else:
        matches = soup.find_all('div', class_='category-item')
    for elem in matches:
        if "models" in item.url:
            url = elem.a['href']
            title = elem.find('div', class_='model-item__desc').text.strip()
            cantidad = elem.find('div', class_='model-item__info-list')
            url += "?sort=-created&p=1"
        elif "channels" in item.url:
            url = elem['href']
            title = elem.img['alt']
            cantidad = elem.find('div', class_='channel__uploaded-videos')
            url += "?sort=-created&p=1"
        else:
            url = elem.a['href']
            title = elem.find('div', class_='category-item__desc').text.strip()
            cantidad = elem.find('div', class_='category-item__info-list')
            url += "?sort=-created&p=1"
        thumbnail = elem.img['data-src']
        url = urlparse.urljoin(item.url,url)
        url += "?sort=-created&p=1"
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='pagination__button')
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
    matches = soup.find_all('app-video-item')
    for elem in matches:
        url = elem['video-href']
        title = elem.img['alt']
        thumbnail = elem.img['data-src']
        if elem.a.get("data-duration", ""):
            time = elem.a['data-duration']
        quality = elem.find('div', class_='video-item__quality')
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
                                  fanart=thumbnail, plot=plot, contentTitle=title ))
    next_page = soup.find('a', class_='pagination__button')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('link', itemprop='contentUrl')['href']
    # url += '|'
    # url += urlparse.urlencode(httptools.default_headers)
    itemlist.append(Item(channel=item.channel, action="play",  contentTitle = item.title, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('link', itemprop='contentUrl')['href']
    # url += '|'
    # url += urlparse.urlencode(httptools.default_headers)
    itemlist.append(['[videosection]' , url])
    return itemlist
