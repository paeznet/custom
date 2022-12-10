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
             'channel': '4kporn', 
             'host': config.get_setting("current_host", '4kporn', default=''), 
             'host_alt': ["https://4kporn.xxx/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel = item.channel,title="Nuevos" , action="lista", url=host + "latest-updates/?sort_by=post_date&from=1"))
    itemlist.append(Item(channel = item.channel,title="Mas vistos" , action="lista", url=host + "most-popular/?sort_by=video_viewed_month&from=1"))
    itemlist.append(Item(channel = item.channel,title="Mejor valorado" , action="lista", url=host + "top-rated/?sort_by=rating_month&from=1"))
    # itemlist.append(Item(channel = item.channel,title="Recomendado" , action="lista", url=host))
    # itemlist.append(Item(channel = item.channel,title="Mas comentado" , action="lista", url=host + "/videos/?sort_by=most_commented&from=1"))
    itemlist.append(Item(channel = item.channel,title="PornStar" , action="categorias", url=host + "models/?sort_by=subscribers_count&from=1"))
    itemlist.append(Item(channel = item.channel,title="Canal" , action="categorias", url=host + "sites/?sort_by=total_videos&from=1"))
    itemlist.append(Item(channel = item.channel,title="Categorias" , action="categorias", url=host + "categories/?sort_by=title&from=1"))
    itemlist.append(Item(channel = item.channel,title="Buscar", action="search"))
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
    matches = soup.find_all('a', class_='item')
    for elem in matches:
        url = elem['href']
        title = elem['title']
        if elem.img:
            thumbnail = elem.img['src']
        else:
            thumbnail = ""
        cantidad = elem.find('div', class_='videos')
        if cantidad and not "pornstars" in url:
            title = "%s (%s)" % (title,cantidad.text.strip())
        if "/channels/" in url:
            url += "?sort_by=post_date&from1=1"
        else:
            url += "?sort_by=post_date&from=1"
        plot = ""
        itemlist.append(Item(channel = item.channel,action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='next')
    if next_page and next_page.find("a"):
        next_page = next_page.a['data-parameters'].split(":")[-1]
        if "from_videos" in item.url:
            next_page = re.sub(r"&from_videos=\d+", "&from_videos={0}".format(next_page), item.url)
        else:
            next_page = re.sub(r"&from=\d+", "&from={0}".format(next_page), item.url)
        itemlist.append(Item(channel = item.channel,action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    matches = soup.find_all('div', class_='item')
    for elem in matches:
        if elem.find('span', class_='line-disabled'):
            continue
        if elem.find('div', class_='ads'):
            continue
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-original']
        time = elem.find('div', class_='duration').text.strip()
        quality = elem.find('span', class_='is-hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel = item.channel,action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('li', class_='next')
    if next_page and next_page.find("a"):
        next_page = next_page.a['data-parameters'].split(":")[-1]
        if "from_videos" in item.url:
            next_page = re.sub(r"&from_videos=\d+", "&from_videos={0}".format(next_page), item.url)
        else:
            next_page = re.sub(r"&from=\d+", "&from={0}".format(next_page), item.url)
        itemlist.append(Item(channel = item.channel,action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel = item.channel,action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

def play(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel = item.channel,action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
