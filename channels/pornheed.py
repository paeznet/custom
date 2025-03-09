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
             'channel': 'pornheed', 
             'host': config.get_setting("current_host", 'pornheed', default=''), 
             'host_alt': ["https://www.pornheed.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "search/recently-added/all-time/all-tubes/all-words/all-duration/explore/1"))
    itemlist.append(Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "search/popular/this-month/all-tubes/all-words/all-duration/explore/1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "search/most-viewed/this-month/all-tubes/all-words/all-duration/explore/1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "search/top-rated/this-month/all-tubes/all-words/all-duration/explore/1"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "search/most-discussed/this-month/all-tubes/all-words/all-duration/explore/1"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/sort-by-name/1"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ss/recently-added/all-time/all-tubes/all-words/all-duration//%s/1" % (host,texto)
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
    matches = soup.find('ul' , class_='auto-grid').find_all('li', id=re.compile(r"\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.img['title']
        thumbnail = elem.img['src']
        cantidad = elem.span
        if cantidad:
            cantidad = scrapertools.find_single_match(cantidad.text, " (\d+) Videos")
            title = "%s (%s)" % (title,cantidad)
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('div', class_='pagelist').find('a', class_='current')
    if next_page and next_page.find_next_sibling("a"):
        next_page = next_page.find_next_sibling("a")['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist

def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('ul' , class_='auto-grid').find_all('li', id=re.compile(r"\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.img['title']
        thumbnail = elem.img['src']
        time = elem.find('div', class_='runtime').text.strip()
        quality = elem.find('div', class_='res')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (time,quality.text,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('div', class_='pagelist').find('a', class_='current')
    if next_page and next_page.find_next_sibling("a"):
        next_page = next_page.find_next_sibling("a")['href']
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
