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
             'channel': 'pornoxo', 
             'host': config.get_setting("current_host", 'pornoxo', default=''), 
             'host_alt': ["https://www.pornoxo.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "videos/newest/1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "videos/most-popular/today/1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "videos/top-rated/1"))
    itemlist.append(Item(channel=item.channel, title="Mas metraje" , action="lista", url=host + "videos/longest/1"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ssearch/%s/?ad_sub=339" % (host,texto)
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
    soup = create_soup(item.url).find('div', class_='tags-box')
    matches = soup.find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.text.strip()
        url = urlparse.urljoin(item.url,url)
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='pagination-next')
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
    matches = soup.find_all('div', class_='video-item-wrapper')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        time = elem.find('span', class_='content-length')
        quality = time.find('span', class_='text-active')
        if time.find('span', class_='member-only'):
            title = "[COLOR red]%s[/COLOR]" % title
        if quality:
            time = scrapertools.find_single_match(str(time),'</span>([^<]+)</span>')
            quality = quality.text.strip()
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (time.strip(),quality,title)
        else:
            time = time.text.strip()
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('link', rel='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron = '"src":"([^"]+)","desc":"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url,quality in matches:
        url = url.replace("\/", "/")
        itemlist.append(Item(channel=item.channel, action="play", title=quality, url=url) )
    return itemlist[::-1]


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron = '"src":"([^"]+)","desc":"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url,quality in matches:
        url = url.replace("\/", "/")
        itemlist.append(['%s' %quality, url])
    return itemlist[::-1]