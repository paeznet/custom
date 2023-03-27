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
             'channel': 'camwhorescloud', 
             'host': config.get_setting("current_host", 'camwhorescloud', default=''), 
             'host_alt': ["https://www.camwhorescloud.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "?sort_by=post_date&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "?sort_by=video_viewed_month&from=01"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "?sort_by=rating_month&from=01"))
    itemlist.append(Item(channel=item.channel, title="Favoritos" , action="lista", url=host + "?sort_by=most_favourited&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "?sort_by=most_commented&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "?sort_by=duration&from=1"))
    itemlist.append(Item(channel = item.channel, title="Categorias" , action="categorias", url=host + "categories/"))
    itemlist.append(Item(channel = item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace("+", "-")
    item.url = "%ssearch/?q=%s&sort_by=post_date&from_videos=01" % (host, texto)
    try:
        return lista(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
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
        if elem.find('span', class_='no-thumb'):
            thumbnail = ""
        else:
            thumbnail = elem.img['src']
        time = elem.find('div', class_='videos').text.strip()
        if not thumbnail.startswith("https"):
            thumbnail = "http:%s" % thumbnail
        url += "?sort_by=post_date&from=01"
        plot = ""
        itemlist.append(Item(channel = item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot=plot) )
    return sorted(itemlist, key=lambda i: i.title)


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
    matches = soup.find_all('div', class_='list-videos')
    matches = matches[-1].find_all('div', class_='item')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-original']
        time = elem.find('div', class_='duration').text.strip()
        private = elem.find('span', class_='line-private')
        if private:
            title = "[COLOR red]%s[/COLOR]" % title
        quality = elem.find('span', class_='is-hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        if not thumbnail.startswith("https"):
            thumbnail = "http:%s" % thumbnail
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel = item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('li', class_='next')
    if next_page:
        next_page = next_page.a['data-parameters'].split(":")[-1]
        if "from_videos" in item.url:
            next_page = re.sub(r"&from_videos=\d+", "&from_videos={0}".format(next_page), item.url)
        else:
            next_page = re.sub(r"&from=\d+", "&from={0}".format(next_page), item.url)
        itemlist.append(Item(channel = item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info(item)
    itemlist = []
    soup = create_soup(item.url)
    if soup.find('div', id='kt_player'):
        url = item.url
    else:
        url = soup.iframe['src']
        url = url.replace("embed", "videos").replace('lol', 'tv')
        name = item.url.split("/")[-2]
        url += "/%s/" %name
    itemlist.append(Item(channel = item.channel, action="play", title= "%s", contentTitle= item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info(item)
    itemlist = []
    soup = create_soup(item.url)
    if soup.find('div', id='kt_player'):
        url = item.url
    else:
        url = soup.iframe['src']
        url = url.replace("embed", "videos").replace('lol', 'tv')
        name = item.url.split("/")[-2]
        url += "/%s/" %name
    itemlist.append(Item(channel = item.channel, action="play", title= "%s", contentTitle= item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
