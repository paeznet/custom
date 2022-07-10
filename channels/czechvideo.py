# -*- coding: utf-8 -*-
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from core import httptools

host = 'http://czechvideo.org'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Ultimos" , action="lista", url=host + "/index.php"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/tags/%s/" % texto
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
    data = scrapertools.find_single_match(data,'<div class="category">(.*?)</ul>')
    patron  = '<li><a href="(.*?)".*?>(.*?)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<div class="short-story">.*?'
    patron += '<a href="([^"]+)" title="([^"]+)">.*?'
    patron += '<img data-src="([^"]+)".*?'
    patron += 'div class="short-time">(.*?)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedurl,scrapedtitle,scrapedthumbnail,scrapedtime in matches:
        title = "[COLOR yellow]" + scrapedtime + "[/COLOR] " + scrapedtitle
        scrapedthumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        scrapedplot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=scrapedurl,
                              thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'<del><a href="([^"]+)">Next</a></del>')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


# <iframe src="//czxxx.org/player/embed_player.php?vid=ghCCizxamK8S"
# https://czxxx.org/f/OasWJlFpwmu3
# https://czxxx.org/e/OasWJlFpwmu3  EMBED
# https://czxxx.org/player/embed_player.php?vid=ghCCizxamK8S
# Referer='https://czechvideo.org/'

# https://waaw.to/player/embed_player.php?vid=ghCCizxamK8S
# https://waaw.to/watch_video.php?vid=ghCCizxamK8S
# https://waaw.to/watch_video.php?v=NHlrYlpuTldTZ1RrUGJtK1lrdGlIQ0FmdS82bEdERDQ0NXhBcmtpbjFvVFVlR3R0d3dWQnUrbnRsR29rb2dNYg%3D%3D#iss=MTkzLjExMS41Mi4xMzA=
# https://waaw.to/watch_video.php?vid=ghCCizxamK8S#iss=MTkzLjExMS41Mi4xMzA=


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data,'<iframe src=".*?vid=([^"]+)"')
    referer = "https://czxxx.org/f/%s" % url

    logger.debug(url)
    url = "https://czxxx.org/player/embed_player.php?vid=%s" % url
    data = httptools.downloadpage(url,  headers={'Referer': host}).data
    url = scrapertools.find_single_match(data,'src: "([^"]+)"')
    url += "|Referer=%s" % referer
    logger.debug(url)
    itemlist.append(item.clone(action="play", contentTitle = item.title, url=url))
    # url = scrapertools.find_single_match(data,'<iframe src="//czxxx.org/player/embed_player.php?vid="([^"]+)"')
    # url = httptools.downloadpage(url).url
    # logger.debug(url)
    # itemlist = servertools.find_video_items(data=data)
    # for videoitem in itemlist:
        # videoitem.title = item.title
        # videoitem.contentTitle = item.contentTitle
        # videoitem.thumbnail = item.thumbnail
        # videoitem.channel = item.channel
    return itemlist

