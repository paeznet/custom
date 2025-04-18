# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup

# Pornlib  

canonical = {
             'channel': 'proporn', 
             'host': config.get_setting("current_host", 'proporn', default=''), 
             'host_alt': ["https://www.proporn.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

#No funcionan el Cookie con ctype y cattype

def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "videos/", ctype="addtime", cattype = "straight"))
    # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "es/videos/", ctype="rating_month", cattype = "straight"))
    # itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host, ctype="comments_month", cattype = "straight"))
    # itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host, ctype="longest", cattype = "straight"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", ctype="addtime", cattype = "straight"))

    # itemlist.append(Item(channel=item.channel, title="", action="", folder=False))

    # itemlist.append(Item(channel=item.channel, title="Trans", action="submenu", cattype="trans"))
    # itemlist.append(Item(channel=item.channel, title="Gay", action="submenu", cattype="gay"))
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
    texto = texto.replace(" ", "-")
    item.url = "%ssearch/%s/?sort_by=post_date&from_videos=01" % (host,texto)
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
    matches = soup.find_all('ul', class_='categories-list')
    hetero =  matches[0]
    matches = hetero.find_all('li', class_='categories-list-item')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text.strip().replace('(', ' (')
        url = urlparse.urljoin(item.url,url)
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_='sites-contain').find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.find('span', class_='denomination').text.strip()
        thumbnail = elem.img['src']
        cantidad = elem.find('span', class_='utter-box')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='pag-next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


# index_filter_sort=comments_day; cattype=straight
def create_soup(url, ctype=None, cattype=None):
    logger.info()
    if "search" in url: 
        headers = {"Cookie": "cattype=%s; index_filter_sort=%s ; search_filter_new=sort=mr&hq=" % (cattype, ctype)}
        data = httptools.downloadpage(url, headers=headers, canonical=canonical).data
    else:
        headers = {"Cookie": "cattype=%s; index_filter_sort=%s; return_to=%ses/; _gat=1" % (cattype, ctype,host), "Referer" : "%ses/" %host}
        data = httptools.downloadpage(url, headers=headers, canonical=canonical).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url, item.ctype, item.cattype)
    matches = soup.find_all('div', class_='thumb')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-original']
        time = elem.find('span', class_='duration-badge').text.strip()
        quality = elem.find('span', class_='hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('ul', class_='pagination').find_all('a')[-1]
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]",
                             cookie=item.cookie, url=next_page) )
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
