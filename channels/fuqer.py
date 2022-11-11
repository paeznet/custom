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

import xbmc
import xbmcgui

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup

canonical = {
             'channel': 'fuqer', 
             'host': config.get_setting("current_host", 'fuqer', default=''), 
             'host_alt': ["https://www.fuqer.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/page1.html"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/most-viewed/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/top-rated/"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "/longest/"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "/most-discussed/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/channels/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%s//search/videos/%s/newest/" % (host,texto)
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
    matches = soup.find('div', class_='thumbs_list').find_all('div', class_='item')
    for elem in matches:
        logger.debug(elem)
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-src']
        cantidad = elem.find('div', class_='label')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        # url = urlparse.urljoin(item.url,url)
        # thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='item-pagin is_last')
    if next_page:
        next_page = next_page.a['data-parameters'].replace(":", "=").split(";").replace("+from_albums", "")
        next_page = "?%s&%s" % (next_page[0], next_page[1])
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    matches = soup.find_all('div', class_='video_item')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-src']
        time = elem.find('span', class_='time').text.strip()
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
    next_page = soup.find('li', class_='next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('source', type='video/mp4')['src']
    # url += "|verifypeer=false"
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


# def play(item):
    # logger.info()
    # itemlist = []
    # soup = create_soup(item.url)
    # url = soup.find('source', type='video/mp4')['src']
    # url += "|Referer=%s" % item.url
    # url += "|verifypeer=false"
    # itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('source', type='video/mp4')['src']
    url += "|Referer=%s" % item.url
    listitem = xbmcgui.ListItem(item.title)
    listitem.setArt({'thumb': item.thumbnail, 'icon': "DefaultVideo.png", 'poster': item.thumbnail})
    listitem.setInfo('video', {'Title': item.title, 'Genre': 'Porn', 'plot': '', 'plotoutline': ''})
    listitem.setMimeType('application/vnd.apple.mpegurl')
    listitem.setContentLookup(False)
    return xbmc.Player().play(url, listitem)
