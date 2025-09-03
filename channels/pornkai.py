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
             'channel': 'pornkai', 
             'host': config.get_setting("current_host", 'pornkai', default=''), 
             'host_alt': ["https://pornkai.com/"], 
             'host_black_list': [], 
             # 'pattern': ['href="?([^"|\s*]+)["|\s*]\s*rel="?stylesheet"?'], 
             'set_tls': None, 'set_tls_min': None, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "api?query=full+movie&sort=new&method=search&page=0"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "api?query=full+movie&sort=best&method=search&page=0"))
    itemlist.append(Item(channel=item.channel, title="Featured" , action="lista", url=host + "api?query=_best&sort=best&method=search&page=0"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "all-categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%sapi?query=%s&sort=new&method=search&page=0" % (host,texto)
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
    matches = soup.find_all('div', class_='thumbnail')
    for elem in matches:
        url = elem.a['href'] #/videos?q=big-tits       
        title = elem.find('div', class_='category_thumbnail_title').text.strip()
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-src']
        url = url.replace("/videos?q=", "")
        url = "%sapi?query=%s&sort=new&method=search&page=0" %(host,url)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return sorted(itemlist, key=lambda i: i.title)


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
        data = re.sub(r"\\n|\\r|\\t|\\\"|\s{2}|-\s", "", data)
    else:
        data = httptools.downloadpage(url).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url, referer="json")
    matches = soup.find_all('div', class_='thumbnail')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('div', class_='vidinfo').a.text.strip()
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-src']
        time = elem.find('div', class_='thumbnail_video_length').text.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title,  contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    current_page = scrapertools.find_single_match(item.url, ".*?&page=(\d+)")
    next_page = int(current_page) + 1
    if next_page:
        next_page = re.sub(r"&page=\d+", "&page={0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('iframe', id='video2')['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('iframe', id='video2')['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
