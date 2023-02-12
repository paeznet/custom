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
             'channel': 'pornhd8k', 
             'host': config.get_setting("current_host", 'pornhd8k', default=''), 
             'host_alt': ["https://pornhd8k.net/"], 
             'host_black_list': [], 
             'pattern': ['this.base_url\s*=\s*"?([^"|\s*]+)["|\s*]'], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "porn-hd-videos"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "most-popular/?sort_by=video_viewed_month&from=01"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "top-rated/1/?sort_by=rating_month&from=01"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "most-commented/1/?sort_by=most_commented_month&from=01"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "models/?sort_by=avg_videos_popularity&from=01"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "sites/?sort_by=avg_videos_popularity&from=01"))

    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/?sort_by=avg_videos_popularity&from=01"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ssearch/%s/" % (host,texto)
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
    matches = soup.find('div', class_='thumbs-holder').find_all('div', class_='item')
    if "models" in item.url:
        matches.pop(0)
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        cantidad = elem.find('span', class_='text')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='item-pagin is_last')
    if next_page:
        next_page = next_page.a['data-parameters'].replace(":", "=").split(";")
        next_page = "?%s&%s" % (next_page[0], next_page[1])
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
    matches = soup.find_all('div', class_='ml-item')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-original']
        quality = elem.find('span', class_='mli-quality')
        if quality:
            title = "[COLOR red]HD[/COLOR] %s" % title
        # logger.debug(thumbnail)
        # thumbnail = scrapertools.find_single_match(thumbnail, '".*?url=([^"]+)"')
        thumbnail=  urlparse.urljoin(item.url,thumbnail)
        url=  urlparse.urljoin(item.url,url)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('ul', class_='pagination').find('li', class_='active')
    if next_page:
        next_page = next_page.find_next('li').a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist



# https://en2.pornhd8k.net/movies/brazzers-ember-snow-mick-blue-the-assman-s-anal-exam-1-3-2022
#       <input type="hidden" value="GH72F72FAR67VFBA" class="3176118d-fcec-4e2f-b11b-7348260c1cfb" />

# https://en2.pornhd8k.net/ajax/get_sources/GH72F72FAR67VFBA/e4d45a071f751cb77d7b589463849d10?count=1&mobile=false&t=1646130680
# https://cdn-us-1.embeddrive.net/playlists/f0d1aec0-f6b9-4b1d-bab4-435a2e5652ee/cf.m3u8


def play(item):
    logger.info()
    video_urls = []
    soup = create_soup(item.url).video
    matches = soup.find_all('source')
    for elem in matches:
        url = elem['src']
        quality = elem['label']

        video_urls.append(['%s' %quality, url])
    video_urls.sort(key=lambda item: int( re.sub("\D", "", item[0])))

    # itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return video_urls
