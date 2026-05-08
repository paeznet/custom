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
             'channel': 'publicsexhub', 
             'host': config.get_setting("current_host", 'publicsexhub', default=''), 
             'host_alt': ["https://publicsexhub.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "videos/q?orderBy=createdAt&sort=desc&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "videos/q?orderBy=views&sort=desc&page=1"))
    # itemlist.append(Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "videos/q?orderBy=duration&sort=desc&page=1"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars/q?orderBy=count&sort=desc&page=1"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch/%s/q?orderBy=createdAt&sort=desc" % (host,texto)
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
    matches = soup.find('div', class_='grid').find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.header.text.strip()
        if elem.find('span', class_='no-thumb'):
            thumbnail = ""
        else:
            thumbnail = elem.img['src']
            thumbnail = scrapertools.find_single_match(thumbnail, '=(.*?)&')
            thumbnail = urlparse.unquote(thumbnail)
        # if "gif" in thumbnail:
            # thumbnail = elem.img['data-src']
        # if not thumbnail.startswith("https"):
            # thumbnail = "https:%s" % thumbnail
        cantidad = elem.p
        if cantidad:
            cantidad = cantidad.text.strip().replace(" videos", "")
            title = "%s (%s)" % (title,cantidad)
        url = urlparse.urljoin(item.url,url)
        if not "/actor/" in url:
            url += "?filter=latest"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('nav', attrs={"aria-label": "Paginación"})
    if next_page:
        next_page = next_page.find_all('a')[-1]['href']
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
    matches = soup.find_all('a', href=re.compile("/(?:es/|)video/[A-z0-9-]+(?:/|)"))
    for elem in matches:
        url = elem['href']
        title = elem.img['title']
        thumbnail = elem.img['src']
        thumbnail = scrapertools.find_single_match(thumbnail, '=(.*?)&')
        thumbnail = urlparse.unquote(thumbnail)
        data = elem.find_all('span', class_='p-1')
        time = data[1].text.strip()
        quality = data[0].text.strip()
        pornstars = elem.find_all('span', class_='whitespace-nowrap')
        for x , value in enumerate(pornstars):
            pornstars[x] = value.text.strip()
        if pornstars:
            pornstar = ' & '.join(pornstars)
            pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
            title = "%s %s" % (pornstar,title)
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
    next_page = soup.find('nav', attrs={"aria-label": "Paginación"})
    if next_page:
        next_page = next_page.find_all('a')[-1]['href']
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
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
