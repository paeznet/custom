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
canonical = {
             'channel': 'Yespornvip', 
             'host': config.get_setting("current_host", 'Yespornvip', default=''), 
             'host_alt': ["https://yesporn.vip/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "search/?sort_by=post_date&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "search/?sort_by=video_viewed&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "search/?sort_by=rating&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "search/?sort_by=most_commented&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Favoritos" , action="lista", url=host + "search/?sort_by=most_favourited&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "search/?sort_by=duration&from_videos=1"))

    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "models/?sort_by=total_videos&from=1"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "channels/?sort_by=total_videos&from=1"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/?sort_by=title&from=1" ))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch/?q=%s&sort_by=post_date&from_videos=1" % (host,texto)
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
    matches = soup.main.find('div', class_='thumbs').find_all('div', class_='thumb')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        if elem.find('span', class_='no-thumb'):
            thumbnail = ""
        else:
            thumbnail = elem.img['src']
        cantidad = elem.find('div', class_='thumb-item')
        if cantidad:
            title = "%s %s" %(title, cantidad.text.split())
        url += "?filter=post_date&from=1"
        plot = ""
        if not "tag" in url:
            itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                                 fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['data-parameters'].split(":")[-1]
        if "from_videos" in item.url:
            next_page = re.sub(r"&from_videos=\d+", "&from_videos={0}".format(next_page), item.url)
        else:
            next_page = re.sub(r"&from=\d+", "&from={0}".format(next_page), item.url)
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
    matches = soup.main.find('div', class_='thumbs').find_all('div', class_='thumb')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        if "PRIVACY POLICY" in title:
            continue
        if elem.find('span', class_='no-thumb'):
            thumbnail = ""
        else:
            thumbnail = elem.img['src']
        if "base64" in thumbnail:
            thumbnail = elem.img['data-original']
        time = elem.find('div', class_='time').text.strip()
        quality = elem.find('div', class_='qualtiy')
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
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['data-parameters'].split(":")[-1]
        if "from_videos" in item.url:
            next_page = re.sub(r"&from_videos=\d+", "&from_videos={0}".format(next_page), item.url)
        else:
            next_page = re.sub(r"&from=\d+", "&from={0}".format(next_page), item.url)
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
    if soup.find_all('a', href=re.compile("/models/[A-z0-9-]+/")):
        pornstars = soup.find_all('a', href=re.compile("/models/[A-z0-9-]+/"))
        for x , value in enumerate(pornstars):
            pornstars[x] = value.text.strip()
        pornstar = ' & '.join(pornstars)
        pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
        plot = ""
        if len(pornstars) <= 3:
            lista = item.contentTitle.split()
            if "HD" in item.title:
                lista.insert (4, pornstar)
            else:
                lista.insert (2, pornstar)
            item.contentTitle = ' '.join(lista)
        else:
            plot = pornstar
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s" , contentTitle=item.contentTitle, url=item.url)) 
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    return itemlist
