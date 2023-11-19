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
from core import jsontools
from bs4 import BeautifulSoup



canonical = {
             'channel': 'pornmd', 
             'host': config.get_setting("current_host", 'pornmd', default=''), 
             'host_alt': ["https://www.pornmd.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

# +20
# https://www.pornmd.com/api/v1/video-search?start=20&query=big%20natural%20tits&orientation=straight
# https://www.pornmd.com/api/v1/video-search?sources=redtube&start=80&query=big%20natural%20tits&orientation=straight
# https://www.pornmd.com/api/v1/video-search?most_recent=1&start=60&query=big%20natural%20tits&orientation=straight
# https://www.pornmd.com/straight/big+natural+tits?most_recent=1&start=0

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Buscar Nuevos" , action="search", orientation="straight", ver = 1))
    itemlist.append(Item(channel=item.channel, title="Buscar Mejor valorados" , action="search", orientation="straight"))
    itemlist.append(Item(channel=item.channel))
    itemlist.append(Item(channel=item.channel, title="Buscar Nuevos Trans" , action="search", orientation="tranny", ver = 1))
    itemlist.append(Item(channel=item.channel, title="Buscar Mejor valorados Trans" , action="search", orientation="tranny"))
    itemlist.append(Item(channel=item.channel))
    itemlist.append(Item(channel=item.channel, title="Buscar Nuevos Gay" , action="search", orientation="gay", ver = 1))
    itemlist.append(Item(channel=item.channel, title="Buscar Mejor valorados Gay" , action="search", orientation="gay"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    latest = ""
    if item.ver:
        latest = "most_recent=1&"
    # item.url = "%sapi/v1/video-search?%squery=%s&orientation=%s&start=0" % (host, latest, texto, item.orientation)
    item.url = "%s%s/%s?%sstart=0" % (host, item.orientation, texto, latest)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


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
    matches = soup.find_all('div', class_='thumb-holder')
    for elem in matches:
        elem = elem.parent
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['data-src']
        time = elem.find('p', class_='vid-length').text.strip()
        source = elem.find('p', class_='vid-source').text.strip()
        title = "[COLOR yellow]%s[/COLOR] [%s] %s"  %(time,source,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='active')
    if next_page and next_page.find_next_sibling("li"):
        next_page = next_page.find_next_sibling("li").a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    url = httptools.downloadpage(item.url, follow_redirects=False, only_headers=True).headers.get("location", "")#).url
    url = url.replace("www.redtube", "es.redtube")
    url = httptools.downloadpage(item.url).url
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    url = httptools.downloadpage(item.url, follow_redirects=False, only_headers=True).headers.get("location", "")#).url
    url = url.replace("www.redtube", "es.redtube")
    # logger.debug(url)
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
