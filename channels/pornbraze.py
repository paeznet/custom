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
             'channel': 'pornbraze', 
             'host': config.get_setting("current_host", 'pornbraze', default=''), 
             'host_alt': ["https://pornbraze.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "videos/"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "videos/viewed/month/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "videos/rated/month/"))
    itemlist.append(Item(channel=item.channel, title="Favoritos" , action="lista", url=host + "videos/favorited/"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "videos/discussed/"))
    itemlist.append(Item(channel=item.channel, title="Mas descargado" , action="lista", url=host + "videos/downloaded/"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "videos/longest/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/?order=alphabetical"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ssearch/video/?s=%s&o=recent" % (host,texto)
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
    matches = soup.find_all('li', id=re.compile(r"^video-category-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = ""
        cantidad = elem.find('div', class_='category-videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
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
    matches = soup.find_all('li', id=re.compile(r"^video-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-original']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        time = elem.find('span', class_='duration').text.strip()
        quality = elem.find('span', class_='is-hd')
        if "HD" in time:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time.replace("HD ", ""),title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', title=re.compile(r"next"))
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron = "{'src':'([^']+)','type':'video/mp4','label':'(\d+p)'"
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url, quality in matches:
        itemlist.append(Item(channel=item.channel, action="play", title= quality, contentTitle = item.contentTitle, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron = 'href="/pornstar/[^"]+">([^<]+)'
    pornstars = re.compile(patron,re.DOTALL).findall(data)
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    lista = item.contentTitle.split()
    if "HD" in item.title:
        lista.insert (4, pornstar)
    else:
        lista.insert (2, pornstar)
    item.contentTitle = ' '.join(lista)
    
    patron = "{'src':'([^']+)','type':'video/mp4','label':'(\d+p)'"
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url, quality in matches:
        itemlist.append(['.mp4 %s' %quality, url])
    return itemlist
