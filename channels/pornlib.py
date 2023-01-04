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
             'channel': 'pornlib', 
             'host': config.get_setting("current_host", 'pornlib', default=''), 
             'host_alt': ["https://www.pornlib.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host, ctype="addtime", cattype = "straight"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host, ctype="rating_month", cattype = "straight"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host, ctype="comments_month", cattype = "straight"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host, ctype="longest", cattype = "straight"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", ctype="addtime", cattype = "straight"))

    itemlist.append(Item(channel=item.channel, title="", action="", folder=False))

    itemlist.append(Item(channel=item.channel, title="Trans", action="submenu", cattype="trans"))
    itemlist.append(Item(channel=item.channel, title="Gay", action="submenu", cattype="gay"))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host, ctype="addtime", cattype=item.cattype))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host, ctype="rating_month", cattype=item.cattype))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host, ctype="comments_month", cattype=item.cattype))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host, ctype="longest", cattype=item.cattype))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories", cattype=item.cattype))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", ctype="addtime", cattype=item.cattype))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch/videos/%s/" % (host,texto)
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
    if "gay" in item.cattype:
        matches = soup.find('div', class_='cat_box_gay').find_all('a')
    elif "trans" in item.cattype:
        matches = soup.find('div', class_='cat_box_trans').find_all('a')
    else:
        matches = soup.find('div', class_='cat_box_straight').find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.text
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url,url)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return itemlist


def create_soup(url, ctype=None, cattype=None):
    logger.info()
    if "search" in url: 
        headers = {"Cookie": "cattype=%s; index_filter_sort=%s ; search_filter_new=sort=mr&hq=" % (cattype, ctype)}
        data = httptools.downloadpage(url, headers=headers, canonical=canonical).data
    else:
        headers = {"Cookie": "cattype=%s; index_filter_sort=%s" % (cattype, ctype)}
        data = httptools.downloadpage(url, headers=headers, canonical=canonical).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url, item.ctype, item.cattype)
    matches = soup.find_all('div', class_='th')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        time = elem.find('span', class_='by').text.strip()
        quality = elem.find('i', class_='icon-hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        url = urlparse.urljoin(item.url,url)
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='item_page selected')
    if next_page and next_page.find_next_sibling("li"):
        next_page = next_page.find_next_sibling("li").a['href']
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
