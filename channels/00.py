# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

canonical = {
             'channel': 'poroyal', 
             'host': config.get_setting("current_host", 'poroyal', default=''), 
             'host_alt': ["https://poroyal.com"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s*rel="?stylesheet"?'], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/videos?o=mr"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "?do=most-viewed&th=month"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "?do=most-rated&th=month"))
    itemlist.append(Item(channel=item.channel, title="1080-4K" , action="lista", url=host + "?do=1080-4k"))
    # itemlist.append(Item(channel=item.channel, title="Mas comentados" , action="lista", url=host + "/most-discussed/")) 
    itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "channels"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="pornstar", url=host + "pornstars?do=most-rated"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?query=%s" % (host, texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def catalogo(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<h3 class="middle-video-container-h3-dt">.*?'
    patron += '<a href="([^"]+)"><img src="([^"]+)".*?'
    patron += 'class="middle-video-container-aa-channels">([^<]+)<.*?'
    patron += '</i>([^<]+)<.*?'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle, cantidad in matches:
        title = "%s (%s)" %(scrapedtitle,cantidad)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    next_page = scrapertools.find_single_match(data, "<li><a href='([^']+)' id='next_previous'")
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def pornstar(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<li><a href=\'([^\']+)\'><img src=\'([^\']+)\'.*?'
    patron += '>([^<]+)</a></h2>.*?'
    patron += '</i> ([^<]+) &'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,cantidad in matches:
        title = "%s (%s)" %(scrapedtitle,cantidad)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    next_page = scrapertools.find_single_match(data, "<li><a href='([^']+)' id='next_previous'")
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="pornstar", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<li>\s*<a href="([^"]+)"><img src="([^"]+)".*?'
    patron += '>([^<]+)</a></h2>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<div class="col-6 col-sm-6 col-md-4 col-lg-4 col-xl-3">.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)" title="([^"]+)".*?'
    patron += '<div class="duration">(.*?)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,time in matches:
        quality = ""
        if "HD" in time:
            quality = "HD"
            time = time.replace("<span class=\"hd-text-icon\">HD</span>", "")
        time = time.strip()
        title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (time, quality, scrapedtitle)
        thumbnail = scrapedthumbnail
        # thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<li class="page-item"><a class="page-link" href="([^"]+)" class="prevnext">')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<source src="([^"]+)" type=\'video/mp4\' label=\'([^\']+)\''
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url,quality in matches:
        itemlist.append(['.mp4 %s' %quality, url])
    return itemlist

