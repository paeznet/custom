# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from core import urlparse


canonical = {
             'channel': 'pornrewind', 
             'host': config.get_setting("current_host", 'pornrewind', default=''), 
             'host_alt': ["https://www.pornrewind.com/"], 
             'host_black_list': [], 
             # 'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 3, 'cf_assistant': False, 
             'set_tls': False, 'set_tls_min': False, 'retries_cloudflare': 5, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

# Videos que no existen.

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "videos/?sort_by=post_date"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorados" , action="lista", url=host + "videos/?sort_by=rating"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "videos/?sort_by=video_viewed"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/?sort_by=total_videos"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ssearch/%s/" % (host,texto)
    try:
        return lista(item)
    except Exception:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron  = '<a class="thumb-categories" href="([^"]+)" title="([^"]+)".*?'
    patron  += 'data-src="([^"]+)".*?'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        scrapedplot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, plot=scrapedplot) )
    itemlist.sort(key=lambda x: x.title)
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron = '<a class="thumb" href="([^"]+)" title="([^"]+)".*?'
    patron += '<img class="lazyload" data-src="([^"]+)".*?'
    patron += '<span>(.*?)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail,scrapedtime in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        logger.debug(url)
        title = "[COLOR yellow]" + scrapedtime + "[/COLOR] " + scrapedtitle
        thumbnail = scrapedthumbnail
        plot = ""
        action = "play"
        if logger.info() is False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                              fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<li class="direction"><a href="([^"]+)" data-ajax="pagination">')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page ) )
    return itemlist


def findvideos(item):
    logger.info(item)
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data= scrapertools.find_single_match(data, '<div class="player">(.*?)<div class="media-info">')
    patron = '<(?:IFRAME SRC|iframe src)="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl in matches:
        url=scrapedurl
    if "kt_player" in data:
        url = item.url
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle= item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info(item)
    itemlist = []
    data = httptools.downloadpage(item.url).data
    logger.debug(data)
    data= scrapertools.find_single_match(data, '<div class="player">(.*?)<div class="media-info">')
    patron = '<(?:IFRAME SRC|iframe src|source src)="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl in matches:
        url=scrapedurl
    if "kt_player" in data:
        url = item.url
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle= item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist