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
             'channel': 'definebabe', 
             'host': config.get_setting("current_host", 'definebabe', default=''), 
             'host_alt': ["https://www.definebabe.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "videos/page1/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "videos/by-rate/page1/"))
    itemlist.append(Item(channel=item.channel, title="Favoritos" , action="lista", url=host + "?sort_by=most_favourited&from=1"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "babes/page1/")) #?filter=c0h0b0e0l0g0
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "sites/page1/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%sview/%s/page1/" % (host,texto)
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
    matches = soup.find_all('div', class_=re.compile(r"^models-[a-z]+__col"))
    for elem in matches:
        url = elem.a['href']
        if "babes/" in item.url:
            title = elem.find('a', class_='mb-1').text.strip()
        else:
            title = elem.p.text.strip()
        if elem.find('span', class_='no-thumb'):
            thumbnail = ""
        else:
            thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-src']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        if "categories/" in item.url:
            cantidad = elem.find('span', class_='video')
        else:
            cantidad = elem.find('span', class_='photo')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    if "categories/" in item.url:
        itemlist.sort(key=lambda x: x.title)
    next_page = soup.find("a", string=re.compile(r"^Next"))
    if next_page:
        next_page = next_page['href']
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
    matches = soup.find_all('div', class_='models-videos__col')
    for elem in matches:
        url = elem.a['href']
        title = elem.p.text.strip()
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-original']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        time = elem.find('img', src=re.compile("/video.svg"))
        if time:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time.parent.text.strip(),title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find("a", string=re.compile(r"^Next"))
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
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
    pornstars = soup.find('div', class_='information').find_all('a', href=re.compile("/models/[A-z0-9]+/[A-z0-9-]+/"))
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    lista = item.contentTitle.split()
    if "[COLOR yellow" in item.title:
        lista.insert (2, pornstar)
    else:
        lista.insert (0, pornstar)
    item.contentTitle = ' '.join(lista)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
