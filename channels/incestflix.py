# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from core import jsontools
from bs4 import BeautifulSoup


canonical = {
             'channel': 'incestflix', 
             'host': config.get_setting("current_host", 'incestflix', default=''), 
             'host_alt': ["https://incestflixx.com/"], 
             'host_black_list': [], 
             'pattern': ["<a href='?([^'|\s*]+)['|\s*]"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
if not host.startswith("http"):
    host = "http:%s" % host


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "page/1"))
    itemlist.append(Item(channel=item.channel, title="Studio" , action="categorias", url=host + "Studio"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "model"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "category"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%spage/1/?s=%s" % (host,texto)
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
    matches = soup.find('div', class_='videos').find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.find('span', class_='name').text.strip()
        thumbnail = elem['style']
        thumbnail = scrapertools.find_single_match(thumbnail, "url\('([^')]+)")
        if "actor/" in url:
            thumbnail = ""
        cantidad = elem.find('span', class_='count')
        if cantidad:
            cantidad = cantidad.text.strip().replace(" Videos", "")
            title = "%s (%s)" %(title, cantidad)
        url += "page/1"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
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
    matches = soup.find_all('a', class_="video")
    for elem in matches:
        url = elem['href']
        title = elem['title']
        thumbnail = elem['style']
        thumbnail = scrapertools.find_single_match(thumbnail, "url\('([^')]+)")
        time = elem.find('span', class_='time')
        if time:
            time = time.text.strip()
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
           
        if time.startswith(":") : continue 
        plot = ""
        itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail,
                                   plot=plot, fanart=thumbnail, contentTitle=title ))
    
    next_page = soup.find("a", string=re.compile(r"^Next"))
    if next_page:
        next_page = next_page['href']
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s" , contentTitle=item.contentTitle, url=item.url)) 
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    if soup.find('div', class_='model-list'):
        pornstars = soup.find('div', class_='model-list').find_all('a', href=re.compile("/actor/[A-z0-9-]+(?:/|)"))
        
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        
        pornstar = ' & '.join(pornstars)
        pornstar = "[COLOR cyan]%s" % pornstar
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = ' %s' %pornstar
        lista.insert (1, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s" , contentTitle=item.contentTitle, url=item.url)) 
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    return itemlist
