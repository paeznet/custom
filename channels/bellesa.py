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
             'channel': 'bellesa', 
             'host': config.get_setting("current_host", 'bellesa', default=''), 
             'host_alt': ["https://www.bellesa.co/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "videos?sort=recent&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "videos?sort=popular&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "videos?sort=longest&page=1"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host ))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "videos/categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch?type=videos&sort=recent&q=%s" % (host,texto)
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
    if "Canal" in item.title:
        matches = soup.header.find_all('a', href=re.compile(r"/channels/"))
    else:
        matches = soup.find_all('div', class_=re.compile(r"^CategoryCard__Container-sc-1xa0lug-\d+"))
    for elem in matches:
        if not "Canal" in item.title:
            url = elem.a['href']
            title = elem.span.text.strip()
            thumbnail = elem.find('div', class_=re.compile(r"^CategoryCard__Thumbnail-sc-1xa0lug-\d+"))['src']
        else:
            url = elem['href']
            title = elem.text.strip()
            thumbnail = ""
        url = urlparse.urljoin(item.url,url)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
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
    matches = soup.find_all('div', class_='kUYGou')
    if "/channels/" in item.url:
        matches.pop(0)
    for elem in matches:
        url = elem.a['href']
        title = elem.h2.text.strip()
        thumbnail = elem.find('div', class_=re.compile(r"^VideoCard__Background-sc-54g127-\d+"))['src']
        time = elem.find('span', class_=re.compile(r"^VideoCard__Duration-sc-54g127-\d+")).text.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        pornstars = elem.find_all('a', href=re.compile(r"performers"))
        for x , value in enumerate(pornstars):
            pornstars[x] = value.text.strip()
        pornstar = ' & '.join(pornstars)
        pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
        lista = title.split()
        if len(pornstars) < 4:
            lista.insert (2, pornstar)
        title = ' '.join(lista)        
        plot = pornstar
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', title="Next page")
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    source = scrapertools.find_single_match(data, '"source":"([^"]+)"')
    resolutions = scrapertools.find_single_match(data, '"resolutions":"([^"]+)"')
    resolutions = resolutions.split(",")
    for quality in resolutions:
        url = "https://s.bellesa.co/v/%s/%s.mp4" %(source,quality)
        itemlist.append(Item(channel=item.channel, action="play", title= quality, contentTitle = item.title, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    source = scrapertools.find_single_match(data, '"source":"([^"]+)"')
    resolutions = scrapertools.find_single_match(data, '"resolutions":"([^"]+)"')
    resolutions = resolutions.split(",")
    for quality in resolutions:
        url = "https://s.bellesa.co/v/%s/%s.mp4" %(source,quality)
        itemlist.append(['%sp' %quality, url])
    return itemlist
