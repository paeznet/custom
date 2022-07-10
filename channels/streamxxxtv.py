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
from channels import autoplay

list_quality = ['default']
list_servers = ['mixdrop']

canonical = {
             'channel': 'streamxxxtv', 
             'host': config.get_setting("current_host", 'streamxxxtv', default=''), 
             'host_alt': ["https://streamxxx.tv"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Peliculas" , action="lista", url=host + "/category/movies-xxx/"))
    itemlist.append(Item(channel=item.channel, title="   Buscar", action="search", cat="4679"))
    itemlist.append(Item(channel=item.channel, title="Videos" , action="lista", url=host + "/category/clips/"))
    itemlist.append(Item(channel=item.channel, title="   Buscar", action="search", cat="5562"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?s=%s&cat=%s" % (host,texto,item.cat)
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
    matches = soup.find_all('article', id=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        plot = ""
        if "new-porn-videos-released" in url:
            action = "lista2"
        else:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista2(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_='stream2')
    matches = str(matches).split('<p> </p>')
    matches.pop(0)
    matches.pop()
    for elem in matches:
        url = scrapertools.find_single_match(elem, 'href="(https://mixdrop[^"]+)"')
        thumbnail = scrapertools.find_single_match(elem,'src="([^"]+)"')
        tdos = scrapertools.find_multiple_matches(elem, '>(?: |)([^<]+)')
        if len(tdos):
            title = tdos[0]
            if title == ' ':
                title = tdos[1]
            itemlist.append(Item(channel=item.channel, action="findvideos", title=title, data=elem, thumbnail=thumbnail, fanart=thumbnail, contentTitle=title ))
    return itemlist

# https://upvideo.to/v/krm1va4b7zhk/SexMex.Emily.Thorne.5.5.2021.1080p.mp4

def findvideos(item):
    logger.info()
    itemlist = []
    repe = []
    if item.data:
        matches = scrapertools.find_multiple_matches(item.data, 'href="([^"]+)"')
        for url in matches:
            if not url in repe and not "upvideo" in url and not "adultempire" in url and not "adshrink" in url and not "keeplinks" in url and not "ouo" in url and not ".rar" in url:
                repe.append(url)
                itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    else:
        soup = create_soup(item.url).find('article')
        matches = soup.find_all(class_='external_icon')
        for elem in matches:
            url = elem['href'].replace("/rg.to/", "/rapidgator.net/")
            if not url in repe and not "adultempire" in url and not "adshrink" in url and not "keeplinks" in url and not "ouo" in url and not ".rar" in url:
                repe.append(url)
                itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist

