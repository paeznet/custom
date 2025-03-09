# -*- coding: utf-8 -*-
#------------------------------------------------------------

from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="gratisiptv" , action="gratisiptv", url="https://www.gratisiptv.com/spain-iptv-free-premium-fhd-channels-08-jun-2020/"))
    return itemlist


def gratisiptv(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<a href="([^"]+)">Download ([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle
        thumbnail = ""
        plot = ""
        itemlist.append(item.clone(action="play", title=title, url=scrapedurl,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    return itemlist
