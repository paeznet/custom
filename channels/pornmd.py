# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
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


# https://www.pornmd.com/c/big-tits?filter%5Border_by%5D=date&page=2

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Buscar Nuevos" , action="search", orientation="straight", ver = "date"))
    itemlist.append(Item(channel=item.channel, title="Buscar Mas vistos" , action="search", orientation="straight", ver = "popular"))
    itemlist.append(Item(channel=item.channel, title="Buscar Mejor valorados" , action="search", orientation="straight", ver = "rating"))
    itemlist.append(Item(channel=item.channel, title="Buscar Mas largo" , action="search", orientation="straight", ver = "duration"))
    itemlist.append(Item(channel=item.channel))
    itemlist.append(Item(channel=item.channel, title="Buscar Nuevos Trans" , action="search", orientation="shemale", ver = "date"))
    itemlist.append(Item(channel=item.channel, title="Buscar Mas vistos Trans" , action="search", orientation="shemale", ver = "popular"))
    itemlist.append(Item(channel=item.channel, title="Buscar Mejor valorados Trans" , action="search", orientation="shemale", ver = "rating"))
    itemlist.append(Item(channel=item.channel, title="Buscar Mas largo Trans" , action="search", orientation="shemale", ver = "duration"))
    itemlist.append(Item(channel=item.channel))
    itemlist.append(Item(channel=item.channel, title="Buscar Nuevos Gay" , action="search", orientation="gay", ver = "date"))
    itemlist.append(Item(channel=item.channel, title="Buscar Mas vistos Gay" , action="search", orientation="gay", ver = "popular"))
    itemlist.append(Item(channel=item.channel, title="Buscar Mejor valorados Gay" , action="search", orientation="gay", ver = "rating"))
    itemlist.append(Item(channel=item.channel, title="Buscar Mas largo Gay" , action="search", orientation="gay", ver = "duration"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    latest = ""
    # item.url = "%sapi/v1/video-search?%squery=%s&orientation=%s&start=0" % (host, latest, texto, item.orientation)
    item.url = "%sc/%s?filter[order_by]=%s&orientation=%s&page=1" % (host, texto, item.ver, item.orientation)
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
    matches = soup.find_all('div', class_='card')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        # title = elem.img['alt']
        texto = elem.find('span', class_='badge').text.strip()
        quality = ""
        if "HD" in texto:
            quality = "HD"
            time = texto.replace("HD", "").strip()
        elif "4K"in texto:
            quality = "4K"
            time = texto.replace("4K", "").strip()
        elif "VR"in texto:
            quality = "VR"
            time = texto.replace("VR", "").strip()
        else:
            time = texto
        source = elem.find('div', class_='item-source-rating-container').a.text.strip()
        thumbnail = elem.img['src']
        title = "[COLOR yellow]%s[/COLOR] [COLOR cyan]%s[/COLOR] [%s] %s"  %(time,quality,source,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('nav', class_='pagination').find_all('a')
    if next_page:
        next_page = next_page[-1]['href']
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
