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
from core import servertools
from core.item import Item
from core import httptools
from channels import filtertools
from channels import autoplay

IDIOMAS = {'vo': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['vidlox']

host = 'https://watchxxxfree.xyz/'

# vidlox y netu al primero le cuesta cargar


def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host + "/?filter=latest"))
    itemlist.append(item.clone(title="Mas vistos" , action="lista", url=host + "/?filter=most-viewed"))
    itemlist.append(item.clone(title="Mas largo" , action="lista", url=host + "/?filter=longest"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append(item.clone(title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?s=%s" % (host, texto)
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
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<article id="post-\d+".*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?'
    patron += 'src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        scrapedplot = ""
        title = scrapedtitle
        itemlist.append(item.clone(action="lista", title=title, url=scrapedurl,
                              thumbnail=scrapedthumbnail , plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<article id="post-\d+".*?'
    patron += '<a href="([^"]+)" title="([^"]+)">.*?'
    patron += '<img data-src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail, in matches:
        title = scrapedtitle
        thumbnail = scrapedthumbnail + "|https://watchxxxfreeinhd.com/" 
        plot = ""
        itemlist.append(item.clone(action="findvideos", title=title, contentTitle = title, url=scrapedurl,
                              thumbnail=thumbnail, plot=plot, fanart=scrapedthumbnail ))
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)">Next')
    if next_page:
        next_page =  urlparse.urljoin(item.url,next_page)
        if "?filtre=date&cat=0" in item.url: next_page += "?filtre=date&cat=0"
        elif "?display=tube&filtre=views" in item.url: next_page += "?display=tube&filtre=views"
        elif "?display=tube&filtre=rate" in item.url: next_page += "?display=tube&filtre=rate"
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    data = scrapertools.find_single_match(data,'<div class="responsive-player">(.*?)</div>')
    patron = 'data-lazy-src="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl in matches:
        if "strdef" in scrapedurl: 
            url = decode_url(scrapedurl)
        else:
            url = scrapedurl
        if not url.startswith("https"):
            url = "https:%s" % url
        if not "xyz/" in url or not "vid=" in url: #netu
            itemlist.append(item.clone(action="play", title = "%s", contentTitle= item.title, url=url ))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language, list_quality)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist


def decode_url(txt):
    import base64
    logger.info()
    itemlist = []
    data = httptools.downloadpage(txt).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    n = 2
    while n > 0:
        b64_url = scrapertools.find_single_match(data, '\(dhYas638H\("([^"]+)"\)')
        b64_url = base64.b64decode(b64_url + "=")
        b64_url = base64.b64decode(b64_url + "==")
        data = b64_url.decode("utf8")
        n -= 1
    url = scrapertools.find_single_match(b64_url, '<iframe src="([^"]+)"')
    url = httptools.downloadpage(url).url
    return url

