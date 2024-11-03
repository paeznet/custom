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

# https://iceporn.tv/     https://randyrooster.com/  https://pornmonde.com/
canonical = {
             'channel': 'randyrooster', 
             'host': config.get_setting("current_host", 'randyrooster', default=''), 
             'host_alt': ["https://randyrooster.com/"], 
             'host_black_list': [], 
             'pattern': ['Logo" src="([^"]+)"'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "hottest-videos"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "most-viewed-videos"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "most-liked-videos"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars?sort=video_count"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "channels?sort=video_count"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories?sort=name"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch?q=%s&sort=hottest" % (host,texto)
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
    matches = soup.find_all('a', class_=re.compile(r"^Single[A-z]+List"))
    for elem in matches:
        url = elem['href']
        title = elem.img['alt']
        if elem.find('span', class_='no-thumb'):
            thumbnail = ""
        else:
            thumbnail = elem.img['src']
        if "gif" in thumbnail or "/placeholders/" in thumbnail:
            thumbnail = elem.img['data-src']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        cantidad = elem.find('div', class_='videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        url += "?sort=hottest&time=W"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find(attrs={"aria-label": "Next"})
    if next_page:
        next_page = next_page['href']
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
    matches = soup.find_all('a', class_='SingleVideoItemLink')
    for elem in matches:
        url = elem['href']
        if not scrapertools.find_single_match(url, '/video/([A-z0-9-]+)'): continue
        title = elem.img['alt']
        thumbnail = elem.img['src']
        if "gif" in thumbnail or "/placeholders/" in thumbnail:
            thumbnail = elem.img['data-src']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        time = elem.find('span', class_='Duration').text.strip()
        quality = elem.find('span', class_='Hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find(attrs={"aria-label": "Next"})
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    url = scrapertools.find_single_match(data, '"file":"([^"]+)"')
    url = url.replace("\/", "/")
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    pornstars= scrapertools.find_single_match(data, 'class="VideoPornstars"(.*?)</ul')
    if pornstars:
        patron = '"Popover">([^<]+)<'
        pornstars = re.compile(patron,re.DOTALL).findall(pornstars)
        pornstar = ' & '.join(pornstars)
        pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
        lista = item.title.split()
        if "HD" in item.title:
            lista.insert (4, pornstar)
        else:
            lista.insert (2, pornstar)
        item.contentTitle = ' '.join(lista)
    
    url = scrapertools.find_single_match(data, '"file":"([^"]+)"')
    url = url.replace("\/", "/")
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
