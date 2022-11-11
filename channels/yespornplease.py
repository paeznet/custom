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
             'channel': 'yespornplease', 
             'host': config.get_setting("current_host", 'yespornplease', default=''), 
             'host_alt': ["https://yespornpleasexxx.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/pornstars/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="canal", url=host ))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/tags/" ))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%s/?s=%s" % (host,texto)
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
    matches = soup.find_all('div', class_='box')
    for elem in matches:
        url = elem.a['href']
        title = elem.figcaption.text.strip()
        thumbnail = elem.img['src']
        if "svg+xml" in thumbnail:
            thumbnail = elem.img['data-src']
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return itemlist



def canal(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="BangBros" , action="lista", url=host + "/bangbros/"))
    itemlist.append(Item(channel=item.channel, title="Brazzers" , action="lista", url=host + "/brazzers/"))
    itemlist.append(Item(channel=item.channel, title="Reality Kings" , action="lista", url=host + "/reality-kings/"))
    soup = create_soup(item.url)
    matches = soup.find('div', class_='text-center').find_all('a', href=re.compile(r"^https://yespornpleasexxx.com/")) #.select('a[href^="https://yespornpleasexxx.com/"]')
    for elem in matches:
        url = elem['href']
        title = elem.text.strip()
        thumbnail = ""
        plot = ""
        if not "tag" in url:
            itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                                 fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
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
    matches = soup.find_all('div', class_='post-preview-styling')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        time = elem.find('p').text.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('div', class_='wp-video')
    url = soup.iframe['src']
    matches = create_soup(url).find_all('source', type='video/mp4')
    for elem in matches:
        url = elem['src']
        itemlist.append(Item(channel=item.channel, action="play", title= "Directo", url=url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


# def play(item):
    # logger.info()
    # itemlist = []
    # soup = create_soup(item.url).find('div', class_='wp-video')
    # url = soup.iframe['src']
    # matches = create_soup(url).find_all('source', type='video/mp4')
    # for elem in matches:
        # url = elem['src']
        # url += "|ignore_response_code=True"
        # itemlist.append(Item(channel=item.channel, action="play", title= "Directo", url=url))
    # return itemlist

def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('div', class_='wp-video')
    url = soup.iframe['src']
    matches = create_soup(url).find_all('source', type='video/mp4')
    for elem in matches:
        url = elem['src']
    url += "|Referer=%s" % item.url
    listitem = xbmcgui.ListItem(item.title)
    listitem.setArt({'thumb': item.thumbnail, 'icon': "DefaultVideo.png", 'poster': item.thumbnail})
    listitem.setInfo('video', {'Title': item.title, 'Genre': 'Porn', 'plot': '', 'plotoutline': ''})
    listitem.setMimeType('application/vnd.apple.mpegurl')
    listitem.setContentLookup(False)
    return xbmc.Player().play(url, listitem)
