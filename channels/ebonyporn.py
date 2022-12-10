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
             'channel': 'ebonyporn', 
             'host': config.get_setting("current_host", 'ebonyporn', default=''), 
             'host_alt': ["http://www.xxx-ebonyporn.com/"], 
             'host_black_list': [], 
             'set_tls': False, 'set_tls_min': False, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

#        FALLA Servidor StresmSB  

def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas visto" , action="lista", url=host + "?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "ebony-porn-actresses/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="canal", url=host + "channels/"))

    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?s=%s&filter=latest" % (host,texto)
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
    matches = soup.find('div', id='primary').find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-src']
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='current')
    if next_page and next_page.parent.find_next_sibling("li"):
        next_page = next_page.parent.find_next_sibling("li").a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def canal(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='sow-image-grid-image')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['data-src']
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
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
    matches = soup.find(id='primary').find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-src']
        time = elem.find('span', class_='duration').text.strip()
        quality = elem.find('span', class_='hd-video')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='current')
    if next_page and next_page.parent.find_next_sibling("li"):
        next_page = next_page.parent.find_next_sibling("li").a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_='responsive-player')
    if matches.find('video'):
        url = matches.video['src']
    else:
        url = matches.iframe['src']
        if "base64" in url:
            url = matches.iframe['data-src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_='responsive-player')
    if matches.find('video'):
        url = matches.video['src']
    else:
        url = matches.iframe['src']
        if "base64" in url:
            url = matches.iframe['data-src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
