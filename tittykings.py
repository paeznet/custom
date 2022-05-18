# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup

canonical = {
             'channel': 'tittykings', 
             'host': config.get_setting("current_host", 'tittykings', default=''), 
             'host_alt': ["https://tittykings.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/latest-updates/?mode=async&function=get_block&block_id=list_videos_latest_videos_list&sort_by=post_date&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/most-popular/?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=video_viewed_month&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/top-rated/?mode=asyncfunction=get_block&block_id=list_videos_common_videos_list&sort_by=rating_month&from=1"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/models/?mode=async&function=get_block&block_id=list_models_models_list&section=&sort_by=model_viewed&from=1"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/channels/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%s/search/%s/?mode=async&function=get_block&block_id=list_videos_videos_list_search_result&category_ids=&sort_by=post_date&from_videos=1" % (host,texto)
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
    if "channels" in item.url:
        matches = soup.find('div', class_='list-channels').find_all('a')
    else:
        matches = soup.find_all('a', class_='item')
    for elem in matches:
        url = elem['href']
        title = elem['title']
        nothumb =  elem.find('span', class_='no-thumb')
        if nothumb:
            thumbnail = ""
        else:
            thumbnail = elem.img['src']
        cantidad = elem.find('div', class_='videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        url += "?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=1" 
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('div', class_='load-more')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    matches = soup.find_all('div', class_='item')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-original']
        time = elem.find('div', class_='duration').text.strip()
        quality = elem.find('span', class_='is-hd"')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('div', class_='load-more')
    if next_page:
        page = next_page.a['data-parameters'].split(':')[-1]
        if "search" in item.url:
            next_page = re.sub(r"&from_videos=\d+", "&from_videos={0}".format(page), item.url)
        else:
            next_page = re.sub(r"&from=\d+", "&from={0}".format(page), item.url)
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
