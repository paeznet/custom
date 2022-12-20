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
from channels import autoplay

IDIOMAS = {'vo': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['gounlimited']

canonical = {
             'channel': 'netpornix', 
             'host': config.get_setting("current_host", 'netpornix', default=''), 
             'host_alt': ["https://netpornix.club"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': True, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host))
    # itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/upcoming-videos/?order=most_views"))
    # itemlist.append(Item(channel=item.channel, title="Proximo" , action="lista", url=host + "/upcoming-videos/?order=newest"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host ))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?s=%s" % (host,texto)
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
    matches = soup.find('ul', class_='g1-secondary-nav-menu').find_all('li', class_='menu-item-object-category')
    for elem in matches:
        url = elem.a['href']
        title = elem.text.strip()
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
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
    soup = create_soup(item.url).find('div', class_='page-body')
    matches = soup.find_all('article')
    for elem in matches:
        logger.debug(elem)
        id = elem['class'][2]
        id = scrapertools.find_single_match(id, 'post-(\d+)')
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title, id=id ))
    next_page = soup.find('li', class_='g1-pagination-item-next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


# https://netpornix.club/full-frontal-caitlin-bell-scarlett-alexis-teamskeet/
# https://netpornix.club/wp-json/wp/v2/posts/57424
# "api_url":"https:\/\/netpornix.club\/wp-json\/wordpress-popular-posts","ID":57424,"token":"174a97503a","lang":0,"debug":0}
# https://netpornix.club/ajax.php?id=57424
# https://netxwatch.xyz/e/qzszcp5fpmou.html
 # https://netxwatch.xyz/sources49/796e456137726f35446e7a487c7c717a737a63703566706d6f757c7c696658776c7169446a4232787c7c73747265616d7362

def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('iframe')
    for elem in matches:
        url = elem['src']
        if "about:blank" in url:
            url= elem['data-lazy-src']
        if "embed.php" in url:
            url = "%s/ajax.php?id=%s"%(host,item.id)
            data = httptools.downloadpage(url).data
            data = data.replace("\\", "")
            url = scrapertools.find_single_match(data, 'src="([^,"]+)"')
        itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist
