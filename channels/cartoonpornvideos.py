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
from core import jsontools
from bs4 import BeautifulSoup

# CAM    https://www.asianpornmovies.com https://www.asspoint.com https://www.mobilepornmovies.com https://movieshark.com https://www.sexoasis.com    https://www.porngash.com 
# https://www.cartoonpornvideos.com https://www.ghettotube.com 
# https://www.lesbianpornvideos.com  https://www.porntv.com https://www.teenieporn.com https://www.youngpornvideos.com
# https://www.porntitan.com 

canonical = {
             'channel': 'cartoonpornvideos', 
             'host': config.get_setting("current_host", 'cartoonpornvideos', default=''), 
             'host_alt': ["https://www.cartoonpornvideos.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel = item.channel,title="Nuevos" , action="lista", url=host + "/videos/straight/all-recent.html"))
    itemlist.append(Item(channel = item.channel,title="Mas vistos" , action="lista", url=host + "/videos/straight/all-view.html"))
    itemlist.append(Item(channel = item.channel,title="Mas popular" , action="lista", url=host + "/videos/straight/all-popular.html"))
    itemlist.append(Item(channel = item.channel,title="Mejor valorado" , action="lista", url=host + "/videos/straight/all-rate.html"))
    itemlist.append(Item(channel = item.channel,title="Mas metraje" , action="lista", url=host + "/videos/straight/all-length.html"))
    itemlist.append(Item(channel = item.channel,title="Parodia" , action="categorias", url=host + "/characters/"))
    itemlist.append(Item(channel = item.channel,title="Canal" , action="categorias", url=host + "/channels/"))

    itemlist.append(Item(channel = item.channel,title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append(Item(channel = item.channel,title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search/video/%s" % (host,texto)
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
    matches = soup.find_all('div', class_="item")
    for elem in matches:
        url = elem.a['href']
        title = elem.find('h2').text
        thumbnail = elem.img['src']
        cantidad = elem.find('div', class_='item-stats')
        videos = elem.find('div', class_='info')
        if videos:
            cantidad = videos.find('span')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        if "popular" in url:
            url = url.replace("popular", "recent")
        if "profile" in url:
            url += "/videos/"
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        if not "/galleries/" in url:
            itemlist.append(Item(channel = item.channel,action="lista", title=title, url=url, fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url).data
        data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_="item")
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        time = elem.find('span', class_='time').text.strip()
        quality = elem.find('span', class_='flag-hd')
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
    next_page = soup.find('div', class_='pagination _767p').find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel = item.channel,action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    m3u = scrapertools.find_single_match(data, 'file: "([^"]+)"')
    data = httptools.downloadpage(m3u).data
    data = data.decode("utf8")
    patron = 'RESOLUTION=\d+x(\d+),.*?'
    patron += '(index-.*?).m3u8'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,url in matches:
        url = m3u.replace("master", url)
        itemlist.append(Item(channel = item.channel,action="play", title=quality, url=url) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    m3u = scrapertools.find_single_match(data, 'file: "([^"]+)"')
    data = httptools.downloadpage(m3u).data
    data = data.decode("utf8")
    patron = 'RESOLUTION=\d+x(\d+),.*?'
    patron += '(index-.*?).m3u8'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,url in matches:
        url = m3u.replace("master", url)
        itemlist.append(['%sp' %quality, url])
    itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return itemlist

