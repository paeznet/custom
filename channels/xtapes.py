# -*- coding: utf-8 -*-
#------------------------------------------------------------
import re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from core import urlparse
from bs4 import BeautifulSoup


forced_proxy_opt = ''
timeout = 45

canonical = {
             'channel': 'xtapes', 
             'host': config.get_setting("current_host", 'xtapes', default=''), 
             'host_alt': ["https://ww2.xtapes.to/"], 
             'host_black_list': ["http://hd.xtapes.to/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 5, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'cf_assistant': False, 'CF_stat': True, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


# Links NetuTV <iframe src=   https://74k.io/e/a9e4rdlxn29v    https://88z.io/#tapgfp

# https://ww2.xtapes.to/bigtits-hd-porn-371770/page/2/?display=tube&filtre=date


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Peliculas" , action="submenu", url=host + "porn-movies-hd/", extra=1))
    itemlist.append( Item(channel=item.channel, title="Videos" , action="submenu", url=host))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    # itemlist.append( Item(channel=item.channel, title="Peliculas" , action="lista", url=host + "porn-movies-hd/"))
    #
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=item.url + "?filtre=date&cat=0"))
    itemlist.append( Item(channel=item.channel, title="Mas Vistos" , action="lista", url=item.url + "?display=tube&filtre=views"))
    itemlist.append( Item(channel=item.channel, title="Mejor valorado" , action="lista", url=item.url + "?display=tube&filtre=rate"))
    itemlist.append( Item(channel=item.channel, title="Longitud" , action="lista", url=item.url + "?display=tube&filtre=duree"))
    if item.extra:
        itemlist.append( Item(channel=item.channel, title="Productora" , action="categorias", url=host))
    else:
        itemlist.append( Item(channel=item.channel, title="Canal" , action="categorias", url=host))
        itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Buscar", url=item.url, action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?s=%s" % (item.url,texto)
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
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    if item.title=="Canal":
        data = scrapertools.find_single_match(data,'<div class="footer-banner">(.*?)<div id="footer-copyright">')
    if item.title=="Productora" :
       data = scrapertools.find_single_match(data,'>Full Movies</a>(.*?)</ul>')
    if item.title=="Categorias" :
       data = scrapertools.find_single_match(data,'<a>Categories</a>(.*?)</ul>')
    patron  = '<a href="([^"]+)">([^"]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapedtitle
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<li class="border-radius-5 box-shadow">.*?'
    patron += 'src="([^"]+)".*?<a href="([^"]+)" title="([^"]+)">.*?'
    patron += '<div class="time-infos".*?>([^"]+)<span class="time-img">'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail,scrapedurl,scrapedtitle,duracion  in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle
        title = "[COLOR yellow]" + duracion + "[/COLOR] " + scrapedtitle
        contentTitle = title
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=item.channel, action="findvideos" , title=title , url=url, thumbnail=thumbnail,
                              fanart=thumbnail, plot=plot, contentTitle = contentTitle))
    next_page = scrapertools.find_single_match(data,'<a class="next page-numbers" href="([^"]+)">Next video')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        next_page = next_page.replace("#038;cat=0#038;", "")
        next_page = next_page.replace("#038;filtre=views#038;", "").replace("&#038;filtre=rate#038;", "&").replace("#038;filtre=duree#038;", "")
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data =scrapertools.find_single_match(data, '"video-embed">(.*?)</div')
    patron = '<(?:IFRAME|iframe) (?:SRC|src)="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url in matches:
        itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
