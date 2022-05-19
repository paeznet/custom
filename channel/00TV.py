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
http://app.powerfhd.me/dash/gets.php?user=hohufoygej&pass=5573373636&t=m3uplus&o=mpegts
http://powerfhd.me/dash/gets.php?user=292159255949199&pass=299994525211497&t=m3uplus&o=mpegts
# http%3A%2F%2Fetbvnogeo-lh.akamaihd.net%2Fi%2FETBSTR2_1%40595582%2Fmaster.m3u8
# http%3A%2F%2Fetbvnogeo-lh.akamaihd.net%2Fi%2FETBSTR1_1%40595581%2Fmaster.m3u8

# http://etbvnogeo-lh.akamaihd.net/i/ETBSTR2_1%40595582/master.m3u8
# http://etbvnogeo-lh.akamaihd.net/i/ETBSTR1_1%40595581/master.m3u8