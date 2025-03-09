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

canonical = {
             'channel': 'hitprn', 
             'host': config.get_setting("current_host", 'hitprn', default=''), 
             'host_alt': ["https://www.hitprn.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "page/1/?orderby=date"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "page/1/?orderby=views"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "page/1/?orderby=likes"))
    # itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "models/?sort_by=avg_videos_popularity&from=01"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%spage/1/?s=%s&orderby=date" % (host,texto)
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
    soup = create_soup(item.url).find('select', id='cat')
    matches = soup.find_all('option', class_=re.compile(r"^level-\d+"))
    for elem in matches:
        cat = elem['value']
        title = elem.text
        if "level-0" in elem['class']:
            title = "[COLOR yellow]%s >>[/COLOR]" %title
        thumbnail = ""
        url = "%spage/1/?cat=%s&orderby=date" %(host,cat)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url, timeout=15).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        # thumbnail += "|verifypeer=false"
        # thumbnail += "|ignore_response_code=True"
        thumbnail += "|Referer=%s" % host
        plot = elem.find('p', class_='entry-summary').text.strip()
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='nextpostslink')
    if next_page:
        next_page = next_page['href']
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
