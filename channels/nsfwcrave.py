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

# https://camcaps.to    https://reallifecam.to  https://voyeur-house.to  https://www.voyeur-house.life/   https://www.nsfwcrave.com/
canonical = {
             'channel': 'nsfwcrave', 
             'host': config.get_setting("current_host", 'nsfwcrave', default=''), 
             'host_alt': ["https://www.nsfwcrave.com/"], 
             'host_black_list': [], 
             'pattern': ['var base_url = "([^"]+)"'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]



def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel = item.channel, title="Videos" , action="submenu", url=host + "videos"))
    itemlist.append(Item(channel = item.channel, title="Cosplay" , action="submenu", url=host + "videos/cosplay"))
    # itemlist.append(Item(channel = item.channel, title="HOT" , action="submenu", url=host + "videos/hot"))
    itemlist.append(Item(channel = item.channel, title="Onlyfans" , action="submenu", url=host + "videos/onlyfans"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "tags"))
    # itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel = item.channel, title="Nuevos" , action="lista", url=item.url + "?o=mr"))
    itemlist.append(Item(channel = item.channel, title="Mas vistos" , action="lista", url=item.url + "?o=mv"))
    itemlist.append(Item(channel = item.channel, title="Mejor valorado" , action="lista", url=item.url + "?o=bw"))
    itemlist.append(Item(channel = item.channel, title="Top favoritos" , action="lista", url=item.url + "?o=tf"))
    itemlist.append(Item(channel = item.channel, title="Mas comentado" , action="lista", url=item.url + "?o=md"))
    itemlist.append(Item(channel = item.channel, title="Mas largo" , action="lista", url=item.url + "?o=lg"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ssearch/videos?search_query=%s" % (host,texto)
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
    matches = soup.find_all('div', class_='tag-item')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text.strip()
        thumbnail = ""
        url = urlparse.urljoin(item.url,url)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
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
    matches = soup.find_all('div', class_='col-sm-6')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['title']
        thumbnail = elem.img['src']
        time = elem.find('div', class_='duration').text.strip()
        quality = elem.find('div', class_='hd-text-icon')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel = item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('i', class_='fa-caret-right')
    if next_page:
        next_page = next_page.parent['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel = item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    url = create_soup(item.url).find('div', class_='video-embedded').iframe['src']
    itemlist.append(Item(channel = item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist