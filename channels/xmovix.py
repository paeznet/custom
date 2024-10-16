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
from core import jsontools as json


canonical = {
             'channel': 'xmovix', 
             'host': config.get_setting("current_host", 'xmovix', default=''), 
             'host_alt': ["http://xmovix.net/"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s*rel="?stylesheet"?'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Escenas" , action="lista", url=host + "en/porno-video//page/1/"))
    itemlist.append(Item(channel=item.channel, title="Peliculas" , action="lista", url=host + "en/movies/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Top 100" , action="lista", url=host + "en/top100.html"))
    itemlist.append(Item(channel=item.channel, title="Full HD" , action="lista", url=host + "en/movies/hd-1080p/page/1/"))
    itemlist.append(Item(channel=item.channel, title="HD" , action="lista", url=host + "en/movies/hd-720p/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Vintage" , action="lista", url=host + "en/movies/vintage/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Parodias" , action="lista", url=host + "en/movies/porno-parodies/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Ruso" , action="lista", url=host + "en/movies/russian-pornostudii/page/1/"))
    itemlist.append(Item(channel=item.channel, title="SUB Ruso" , action="lista", url=host + "en/movies/s-perevodom/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Año" , action="anno"))
    itemlist.append(Item(channel=item.channel, title="Pais" , action="categorias", url=host + "en/", extra="Country" ))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "en/", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%sindex.php?do=search&lang=en&subaction=search&search_start=1&full_search=0&result_from=25&story=%s" % (host,texto)
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
    soup = create_soup(item.url).find('ul', class_='hmenu')
    if "Country" in item.extra:
        matches = soup.find_all('a', href=re.compile(r"/country/"))
    else:
        matches = soup.find_all('div', class_='hidden-menu')[-1].find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.text.strip()
        url = urlparse.urljoin(item.url,url)
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return itemlist


def anno(item):
    logger.info()
    from datetime import datetime
    
    itemlist = []
    
    now = datetime.now()
    year = int(now.year)
    while year >= 1980:
        itemlist.append(item.clone(title="%s" %year, action="lista", url= "%sen/watch/year/%s/" % (host,year)))
        year -= 1
    
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
    if "top100" in item.url:
        matches = soup.find_all('li', class_='top100-item')
    else:
        matches = soup.find_all('div', class_='short-in')  #re.compile(r"^item-\d+")
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['data-src']
        thumbnail = urlparse.urljoin(host,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('span', class_='pnext')
    if next_page and next_page.find('a'):
        if next_page.a.get('id', ''):
            next_page = next_page.a['onclick']
            next_page = scrapertools.find_single_match(next_page, '(\d+)')
            next_page = re.sub(r"&search_start=\d+", "&search_start={0}".format(next_page), item.url)
        else:
            next_page = next_page.a['href']
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    pornstars = soup.find_all('a', href=re.compile("/name/[A-z0-9%20]+/"))
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    plot = pornstar
    
    patron = 's2.src\s*=\s*"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url in matches:
        if not "s2." in url: #NETU
            itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url, plot=plot))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
