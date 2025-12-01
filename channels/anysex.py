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

##   Fallan fotos   https://i2.anysex.com/videos_screenshots/422000/422957/608x342/1.jpg   .replace("608x342", "640x360")

canonical = {
             'channel': 'anysex', 
             'host': config.get_setting("current_host", 'anysex', default=''), 
             'host_alt': ["https://anysex.com/"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s*rel="?alternate"?'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "search/1/?sort=new")) #&q=
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "search/1/?sort=views"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "search/1/?sort=top"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "models/1/?sort=total_videos"))
    itemlist.append(Item(channel=item.channel, title="Caanal" , action="categorias", url=host + "channels/1/?sort_by=total_videos"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/?sort_by=title"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch/1/?sort=new&q=%s" % (host,texto)
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
    matches = soup.find('div', class_='content').find_all(class_='item')
    for elem in matches:
        
        url = elem.a['href'] if elem.find('a') else elem['href']
        title = elem.a['title'] if elem.find('a') else elem['title']
        if elem.find('span', class_='no-thumb'):
            thumbnail = ""
        else:
            thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-src']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        cantidad = elem.find('span', class_='video_count')
        if cantidad:
            cantidad = cantidad.text.strip().replace("videos","")
            title = "%s (%s)" % (title, cantidad)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    if "/categories/" in url:
        itemlist.sort(key=lambda x: x.title)
    next_page = soup.find('div', class_='pagination')
    if next_page:
        next_page = next_page.find_all('a')[-1]['href']
        next_page = urlparse.urljoin(item.url, next_page)
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
    matches = soup.find('div', class_='list-videos').find_all('div', class_='item')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-jpg']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        if "608x342" in thumbnail:
            thumbnail = thumbnail.replace("608x342", "640x360")
        logger.debug(thumbnail)
        time = elem.find('div', class_='duration').text.strip()
        quality = elem.find('span', class_='is-hd')
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('div', class_='pagination')
    if next_page:
        next_page = next_page.find_all('a')[-1]['href']
        next_page = urlparse.urljoin(item.url, next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist



def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    pornstars = soup.find('div', class_='video-tags').find_all('a', href=re.compile("/models/[A-z0-9-]+/"))
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    lista = item.contentTitle.split()
    if "HD" in item.title:
        lista.insert (4, pornstar)
    else:
        lista.insert (2, pornstar)
    item.contentTitle = ' '.join(lista)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
