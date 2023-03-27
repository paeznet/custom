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
             'channel': 'xxxbule', 
             'host': config.get_setting("current_host", 'xxxbule', default=''), 
             'host_alt': ["https://www.xxxbule.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "newest/"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "top-rated/"))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="lista", url=host + "popular/"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "sites/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "streams/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%sfind/%s/newest/" % (host,texto)
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
    matches = soup.find_all('div', class_='style24')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title'].replace(" FREEPORN", "")
        if elem.find('span', class_='no-thumb'):
            thumbnail = ""
        else:
            thumbnail = elem.img['src']
        cantidad = elem.find('div', class_='videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        url += "newest/"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    if  "/streams/" in item.url:
        itemlist.sort(key=lambda x: x.title)
    next_page = soup.find_all('li', class_='style33')
    if next_page:
        next_page = next_page[-1].a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    matches = soup.find_all('div', class_='style24')
    for elem in matches:
        time = elem.find('div', class_='style48').text.strip()
        if "Live" in time:
            continue
        url = elem.a['href']
        url2 = urlparse.urljoin(item.url,url)
        id = elem.a['data-id']
        title = elem.a['title']
        thumbnail = elem.img['src']
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = url.split("/")
        url = "https://www.xxxbule.com/videos/%s/%s.mp4" %(id,url[-2])
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url, url2=url2,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find_all('li', class_='style33')
    if next_page:
        next_page = next_page[-1].a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", contentTitle = item.contentTitle, url=item.url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url2)
    matches = soup.find('div', class_='style72')
    plot = ""
    if matches:
        plot= matches.text.strip()
    itemlist.append(Item(channel=item.channel, action="play", contentTitle = item.contentTitle, url=item.url, plot=plot))
    return itemlist
