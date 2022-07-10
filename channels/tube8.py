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
from core import jsontools
from bs4 import BeautifulSoup

canonical = {
             'channel': 'tube8', 
             'host': config.get_setting("current_host", 'tube8', default=''), 
             'host_alt': ["https://www.tube8.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/newest.html"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/mostviewed.html"))
    itemlist.append(Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "/mostfavorited.html"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/top.html"))
    itemlist.append(Item(channel=item.channel, title="Mas metraje" , action="lista", url=host + "/longest.html"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="catalogo", url=host + "/pornstars/?sort=rl"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/top-channels/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories.html"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/searches.html?q=%s" % (host,texto)
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
    soup = create_soup(item.url)
    matches = soup.find('div', class_='popular_pornstars_wrapper').find_all('div', class_='pornstar')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['data-thumb']
        cantidad = elem.find('li', class_='pornstar-videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', id='pagination_next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    if "categories" in item.url:
        matches = soup.find('ul', id='porn-categories-box').find_all('li')
    else:
        matches = soup.find_all('div', class_='channel')
    for elem in matches:
        url = elem.a['href']
        cantidad = elem.find('div', class_='videos')
        if "channel" in url:
            title = elem.img['alt']
            cantidad = elem.find('span')
        else:
            title = elem.find('h5').text.strip()
            title = title.replace("\s+(", " (")
        thumbnail = elem.img['src']
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url, url)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, fanart=thumbnail, thumbnail=thumbnail) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url).data
        data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)#.find('div', id='category_video_list')
    matches = soup.find_all('figure', id=re.compile(r"^boxVideo_i\d+"))
    a = 8
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['data-thumb']
        quality = elem.find('span', class_='hdIcon')
        time = elem.find('span', class_='video-duration').text.strip()
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time, title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url += "|Referer=%s" % url
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        if a > 0:  #quitar 4 videos fijos menu
            a -= 1
        else:
            itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, contentTitle=title,
                                       fanart=thumbnail, thumbnail=thumbnail ))
    next_page = soup.find('a', id='pagination_next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
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
