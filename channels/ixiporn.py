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
import base64

forced_proxy_opt = 'ProxySSL'

# https://ixiporn.com   https://xvideosdesi.net/   https://www.pornhqxxx.com/  
# https://uncutmaza.com/ 
canonical = {
             'channel': 'ixiporn', 
             'host': config.get_setting("current_host", 'ixiporn', default=''), 
             'host_alt': ["https://ixiporn.info/"], 
             'host_black_list': ["https://ixiporn.com"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

#   los mp4 no funcionan error 403 forbiden y Links caidos solo NUEVOS

def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host )) #+ "/?filter=latest"
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "/?filter=longest"))

    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/porn-category"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?s=%s" % (host,texto)
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
    matches = soup.find_all('div', class_='video-block')
    for elem in matches:
        logger.debug(elem)
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-src']
        cantidad = elem.find('div', class_='video-datas')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='next page-link')
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
    matches = soup.find_all('div', class_='video-block')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('a', class_='infos')['title']
        thumbnail = elem.img['data-src']
        time = elem.find('span', class_='duration')
        if time:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time.text.strip(),title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='next page-link')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('iframe')['data-lazy-src']
    if "ixiporn" in url or "xvideosdesi" in url:
        url = url.split("?q=")
        url = base64.b64decode(url[1]).decode('utf-8')
        url = urlparse.unquote(url)
        url = scrapertools.find_single_match(url, '<(?:source|iframe) src="([^"]+)"')
    url += "|Referer=%s" % host
    itemlist.append(Item(channel=item.channel, action="play", title= url, contentTitle = item.title, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('iframe')['src']
    if "ixiporn" in url or "xvideosdesi" in url:
        url = url.split("?q=")
        url = base64.b64decode(url[1]).decode('utf-8')
        url = urlparse.unquote(url)
        logger.debug(url)
        url = scrapertools.find_single_match(url, '<(?:source|iframe) src="([^"]+)"')
    url += "|Referer=%s" % host
    itemlist.append(Item(channel=item.channel, action="play", title= url, contentTitle = item.title, url=url))
    return itemlist
