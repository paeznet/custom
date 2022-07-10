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

#  https://www.porntube.com    https://www.pornerbros.com   https://www.4tube.com  https://www.fux.com
canonical = {
             'channel': '4tube', 
             'host': config.get_setting("current_host", '4tube', default=''), 
             'host_alt': ["https://www.4tube.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host + "/videos?sort=date"))
    itemlist.append(item.clone(title="Popular" , action="lista", url=host + "/videos?time=month"))
    itemlist.append(item.clone(title="Mas Visto" , action="lista", url=host + "/videos?sort=views&time=month"))
    itemlist.append(item.clone(title="Mas Valorada" , action="lista", url=host + "/videos?sort=rating&time=month"))
    itemlist.append(item.clone(title="Longitud" , action="lista", url=host + "/videos?sort=duration&time=month"))
    itemlist.append(item.clone(title="Pornstars" , action="categorias", url=host + "/pornstars"))
    itemlist.append(item.clone(title="Canal" , action="categorias", url=host + "/channels"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "/tags"))
    itemlist.append(item.clone(title="Buscar", action="search", url= host))

    itemlist.append(Item(channel = item.channel, title = ""))
    itemlist.append(item.clone(title="Trans", action="submenu", orientation="/shemale"))
    itemlist.append(item.clone(title="Gay", action="submenu", orientation="/gay"))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    url = host + item.orientation
    itemlist.append(item.clone(title="Nuevos" , action="lista", url=url + "/videos?sort=date"))
    itemlist.append(item.clone(title="Popular" , action="lista", url=url + "/videos?time=month"))
    itemlist.append(item.clone(title="Mas Visto" , action="lista", url=url + "/videos?sort=views&time=month"))
    itemlist.append(item.clone(title="Mas Valorada" , action="lista", url=url + "/videos?sort=rating&time=month"))
    itemlist.append(item.clone(title="Longitud" , action="lista", url=url + "/videos?sort=duration&time=month"))
    itemlist.append(item.clone(title="Pornstars" , action="categorias", url=url + "/pornstars"))
    itemlist.append(item.clone(title="Canal" , action="categorias", url=url + "/channels"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=url + "/tags"))
    itemlist.append(item.clone(title="Buscar", action="search", url=url))
    
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search?sort=date&q=%s" % (item.url, texto)
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
    matches = soup.find_all('a', class_='thumb-link')
    for elem in matches:
        url = elem['href']
        title = elem['title']
        thumbnail = elem.img['data-original']
        cantidad = elem.find('div', class_='thumb-info').li
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url =urlparse.urljoin(item.url,url)
        plot = ""
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', id='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    soup = create_soup(item.url).find('div', class_='colspan4-content')
    matches = soup.find_all('div', class_='thumb_video')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-original']
        pornstars = elem.find('li', class_='master-pornstar')
        time = elem.find('li', class_='duration-top').text.strip()
        quality = elem.find('li', class_='topHD')
        pornstar = ""
        if pornstars:
            pornstar = " [COLOR cyan]%s[/COLOR]" % pornstars.text.strip()
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR]%s %s" % (time,pornstar,title)
        else:
            title = "[COLOR yellow]%s[/COLOR]%s %s" % (time,pornstar,title)
        url =urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(item.clone(action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', id='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info(item)
    itemlist = []
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info(item)
    itemlist = []
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist