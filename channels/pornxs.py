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
from core import jsontools as json

# OUT 20-6-2024
# http://www.pornxs.net/  parece otro

canonical = {
             'channel': 'pornxs', 
             'host': config.get_setting("current_host", 'pornxs', default=''), 
             'host_alt': ["http://www.pornxs.net/"], 
             'host_black_list': ["https://pornxs.com/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="lista", url=host + "videos?p=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="lista", url=host + "videos?o=v7&p=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorada" , action="lista", url=host + "videos?o=r7&p=1"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "videos?o=l&p=1"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "channels?p=1", id="listChannels"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "models?p=1", id="listProfiles"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories", id="listTags"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%s/search?q=%s&p=1" % (host,texto)
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
    soup = get_source(item.url, soup=True)
    matches = soup.find('ul', class_='%s' %item.id)
    for elem in matches.find_all('li'):
        if elem.find('a', class_='title'):
            url = elem.find('a', class_='title')['href']
            title = elem.find('a', class_='title').text.strip()
        else:
            url = elem.a['href']
            title = elem.find('span', class_='title').text.strip()
        cantidad = elem.find('span', class_='count')
        if cantidad:
            title = "%s (%s)" %(title,cantidad.text.strip())
        if elem.find('img', class_='channel-cover'):
            thumbnail = elem.find_all('source')[-2]['srcset']
        else:
            thumbnail = elem.img['src']
        url = urlparse.urljoin(item.url,url)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find("a", string=re.compile(r"^Next"))
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page, id=item.id) )
    return itemlist


def get_source(url, json=False, soup=False, multipart_post=None, timeout=30, add_host=True, **opt):
    logger.info()
    
    opt['canonical'] = canonical
    data = httptools.downloadpage(url, soup=soup, files=multipart_post, add_host=add_host, timeout=timeout, **opt)
    
    if json:
        data = data.json
    elif soup:
        data = data.soup
    else:
        data = data.data
    
    return data


def lista(item):
    logger.info()
    itemlist = []
    soup = get_source(item.url, soup=True)
    matches = soup.find('ul', class_='listThumbs').find_all('li')
    for elem in matches:
        if elem.find('iframe'): continue
        url = elem.find('a', class_='title')['href']
        title = elem.find('a', class_='title')['title']
        thumbnail = elem.img['src']
        time = elem.find('span', class_='duration').text.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find("a", string=re.compile(r"^Next"))
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data, '"all":"([^"]+)"')
    itemlist.append(['[pornxs]', url])
    # itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data, '"all":"([^"]+)"')
    itemlist.append(['[pornxs]', url])
    # itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
