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

forced_proxy_opt = 'ProxySSL'
timeout = 30

canonical = {
             'channel': 'porner', 
             'host': config.get_setting("current_host", 'porner', default=''), 
             'host_alt': ["https://porner.tv/"], 
             'host_black_list': [], 
             'pattern': ['property="og:image" content="?([^"|\s*]+)["|\s*]'], 
             'set_tls': False, 'set_tls_min': False, 'retries_cloudflare': 3, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "hottest-videos/page/1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "most-viewed-videos/page/1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "most-liked-videos/page/1"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars/page/1"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "channels/page/1"))

    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories?sort=name"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%s/search?q=%s" % (host,texto)
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
    matches = soup.find_all('a', class_=re.compile(r"^Single\w+List"))
    for elem in matches:
        url = elem['href']
        title = elem.img['alt']
        thumbnail = elem.img['data-src']
        url = urlparse.urljoin(host,url)
        url += "/page/1"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='page-item active')
    page = scrapertools.find_single_match(item.url, "(.*?/page/)")
    if next_page:
        next_page = next_page.find_next_sibling('li')
        next_page = "%s%s" % (page, next_page.text)
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
    matches = soup.find_all('a', class_='SingleVideoItemLink')
    for elem in matches:
        url = elem['href']
        title = elem.img['alt']
        thumbnail = elem.img['data-src']
        time = elem.find('span', class_='Duration')
        quality = elem.find('span', class_='Hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time.text.strip(),title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time.text.strip(),title)
        url = urlparse.urljoin(host,url)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="play", title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail, plot=plot))
    next_page = soup.find('li', class_='page-item active')
    page = scrapertools.find_single_match(item.url, "(.*?/page/)")
    if next_page:
        next_page = next_page.find_next_sibling('li')
        next_page = "%s%s" % (page, next_page.text)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    url = scrapertools.find_single_match(data, '"file":"([^"]+)"')
    url = url.replace("\/", "/")
    data = httptools.downloadpage(url).data.decode("utf8")
    patron = 'RESOLUTION=\d+x(\d+),CLOSED-CAPTIONS=NONE\s*([^\s]+)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,url1 in matches:
        videourl = urlparse.urljoin(url,url1)
        # itemlist.append(["[porner]  %sp" % quality, videourl])
        itemlist.append(Item(channel=item.channel, action="play", title= quality, contentTitle = item.title, url=videourl))
    itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data

    pornstars = scrapertools.find_single_match(data, '<div class="VideoPornstars">(.*?)</ul')
    pornstars = scrapertools.find_multiple_matches(pornstars, '<span class="Popover">([^<]+)<')
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    lista = item.title.split()
    if "HD" in item.title:
        lista.insert (4, pornstar)
    else:
        lista.insert (2, pornstar)
    item.contentTitle = ' '.join(lista)

    url = scrapertools.find_single_match(data, '"file":"([^"]+)"')
    url = url.replace("\/", "/")
    data = httptools.downloadpage(url).data.decode("utf8")
    patron = 'RESOLUTION=\d+x(\d+),CLOSED-CAPTIONS=NONE\s*([^\s]+)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,url1 in matches:
        videourl = urlparse.urljoin(url,url1)
        itemlist.append(["[porner]  %sp" % quality, videourl])
    itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return itemlist
