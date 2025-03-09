# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

import xbmc
import xbmcgui
from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup

######################################### OUT  2-2024

canonical = {
             'channel': 'thepornfull', 
             'host': config.get_setting("current_host", 'thepornfull', default=''), 
             'host_alt': ["https://thepornfull.net/"], 
             'host_black_list': ["https://thepornfull.com/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host))
    # itemlist.append(Item(channel=item.channel, title="Mas Vistos" , action="lista", url=host + "mais-vistos/"))
    # itemlist.append(Item(channel=item.channel, title="Mas Votados" , action="lista", url=host + "mais-votados/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host ))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?s=%s" % (host,texto)
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
    matches = soup.find_all('li', class_=re.compile(r"^cat-item-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text.strip()
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
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
    matches = soup.find_all("article", class_=re.compile(r"^post-\d+"))
    for elem in matches:
        # url = elem.a['href']
        id = scrapertools.find_single_match(elem['class'][1], 'post-(\d+)')
        title = elem.h2.text
        thumbnail = elem.img['src']
        if ".gif" in thumbnail:
            thumbnail = elem.img['data-src']
        plot = ""
        url = "%swp-content/plugins/x-player/player.php?v=%s" %(host,id)
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    # next_page = soup.find('li', class_='active')
    next_page = soup.find("a", string=re.compile(r"^Next"))
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    # soup = create_soup(item.url)
    # url = soup.iframe['src']
    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data, 'file: "([^"]+)"')
    url += "|Referer=%s" % item.url
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    listitem = []
    # soup = create_soup(item.url)
    # url = soup.iframe['src']
    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data, 'file: "([^"]+)"')
    url += "|Referer=%s" % item.url
    itemlist.append(['[thepornfull] .mp4', url])
    return itemlist
    