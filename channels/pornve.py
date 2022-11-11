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
             'channel': 'pornve', 
             'host': config.get_setting("current_host", 'pornve', default=''), 
             'host_alt': ["https://pornve.com"], 
             'host_black_list': [], 
             'pattern': ['id="sitelogo" href="?([^"|\s*]+)'], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


# https://pornve.com/?cat_id=6&cat_name=Big%20tits&op=search&sort_field=file_created&sort_order=down&page=1
# https://pornve.com/?cat_name=Big%20tits&sort_field=file_created&sort_order=down&page=1
# file_created    file_rating     file_view         file_length
# https://pornve.com/search/big%20tits/page2
# https://pornve.com/?data_name=&k=big%20natural%20tits&op=search&sort_field=file_rating&sort_order=down&page=2

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host))
    # itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/most-popular/?sort_by=video_viewed_month&from=01"))
    # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/top-rated/1/?sort_by=rating_month&from=01"))
    # itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "/most-commented/1/?sort_by=most_commented_month&from=01"))
    # itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/models/?sort_by=avg_videos_popularity&from=01"))
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/sites/?sort_by=avg_videos_popularity&from=01"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?op=search&k=%s" % (host,texto)
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
    matches = soup.find_all('div', class_='vid_bloczk')
    for elem in matches:
        url = elem.a['href']
        title = elem.b.text.strip()
        thumbnail = elem.a['style']
        cantidad = elem.find('span')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        thumbnail = scrapertools.find_single_match(thumbnail, "(http.*?jpg)")
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    return itemlist


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
    matches = soup.find_all('div', class_='vid_bloczk')
    for elem in matches:
        url = elem.a['href']
        title = elem.b.text.strip()
        thumbnail = elem.a['style']
        thumbnail = scrapertools.find_single_match(thumbnail, "(http.*?jpg)")
        time = elem.span.text.strip()
        quality = elem.find('span', class_='label hd')
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
    next_page = soup.find('div', class_='paging').b
    if next_page and next_page.find_next_sibling("a"):
        next_page = next_page.find_next_sibling("a")['href']
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
