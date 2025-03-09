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

# https://pornovideow.com/    https://2023.pornvideobb.com/

canonical = {
             'channel': 'pornovideow', 
             'host': config.get_setting("current_host", 'pornovideow', default=''), 
             'host_alt': ["https://pornovideow.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "home/?d=09&sort=date"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "home/?d=09&sort=views"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "home/?d=09&sort=liked"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="catalogo", url=host + "porn_actor/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "study/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch_video/?q=%s&sort=date" % (host,texto)
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
    if "study/" in item.url:
        soup = soup.find('div', class_='category-spisok')
    else:
        soup = soup.find('ul', id='category-desctop')
    matches = soup.find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.text.strip()
        thumbnail = ""
        if not url.startswith("https"):
            url = "https:%s" % url
        plot = ""
        if not "English" in title and not "Russian" in title:
            itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                                 fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('li', id='li-actor-set')
    for elem in matches:
        if elem.iframe:
            continue
        url = elem.a['href']
        title = elem.h2.text.strip()
        thumbnail = elem.img['src']
        if not url.startswith("https"):
            url = "https:%s" % url
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='pstr_next')
    if next_page:
        next_page = next_page['href']
        if not next_page.startswith("https"):
            next_page = "https:%s" % next_page
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    matches = soup.find('ul', id='ul-porn-set').find_all('li', id='li-porn-video-set')
    for elem in matches:
        if elem.iframe:
            continue
        block = elem.find('div', class_='block-images-porn-set')
        url = block.a['href']
        title = block.img['alt']
        if title.startswith("Porn video "):
            title = title.replace("Porn video ", "")
        thumbnail = block.img['src']
        if not url.startswith("https"):
            url = "https:%s" % url
        time = elem.find('i', class_='cifra-time-set').text.strip()
        quality = elem.find('span', class_='is-hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='pstr_next')
    if next_page:
        next_page = next_page['href']
        if not next_page.startswith("https"):
            next_page = "https:%s" % next_page
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
    data = httptools.downloadpage(item.url).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    
    pornstars = soup.find_all('a', href=re.compile("&actor=\w+"))
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
    
    url = scrapertools.find_single_match(data, 'id:"player", file:"([^"]+)"')
    itemlist.append(Item(channel=item.channel, action="play", server= "Directo", contentTitle = item.contentTitle, url=url))
    return itemlist
