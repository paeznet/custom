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

# https://pornenix.com/     https://playenix.com/
# https:/daftsex.app/   https://draftsex.porn/


canonical = {
             'channel': 'daftsex', 
             'host': config.get_setting("current_host", 'daftsex', default=''), 
             'host_alt': ["https://daftsex.app/"], 
             'host_black_list': [], 
             'pattern': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "page/1/?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "page/1/?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "page/1/?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "page/1/?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars/page/1/"))
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "studios/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%spage/1/?s=%s&filter=latest" % (host,texto)
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
    matches = soup.find_all('article', class_=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href'].replace("?actors=", "/pornstars/")
        title = elem.a['title']
        if elem.find('span', class_='no-thumb'):
            thumbnail = ""
        else:
            thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-src']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        cantidad = elem.find('div', class_='videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        # url = urlparse.urljoin(item.url,url)
        # thumbnail = urlparse.urljoin(item.url,thumbnail)
        url += "/page/1/?filter=latest"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='current')
    if next_page and next_page.parent.find_next_sibling("li"):
        next_page = next_page.parent.find_next_sibling("li").a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data  #, verifypeer=False
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('article', class_=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-src']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        time = elem.find('span', class_='duration').text.strip()
        quality = elem.find('span', class_='is-hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='current')
    if next_page and next_page.parent.find_next_sibling("li"):
        next_page = next_page.parent.find_next_sibling("li").a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    if soup.find('div', class_='responsive-player').find(re.compile("(?:iframe|source)")):
        url = soup.find('div', class_='responsive-player').find(re.compile("(?:iframe|source)"))['src']
        if "php?q=" in url:
            import base64
            url = url.split('php?q=')
            url_decode = base64.b64decode(url[-1]).decode("utf8")
            url = urlparse.unquote(url_decode)
            url = scrapertools.find_single_match(url, '<(?:iframe|source) src="([^"]+)"')
            itemlist.append(Item(channel=item.channel, action="play", server= "Directo", contentTitle = item.contentTitle, url=url))
    return itemlist



def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    # if soup.find('div', class_='pornstar-list'):
        # pornstars = soup.find('div', class_='pornstar-list').find_all('a', href=re.compile("/pornstars/[A-z0-9-]+/"))
        # for x , value in enumerate(pornstars):
            # pornstars[x] = value.text.strip()
        # pornstar = ' & '.join(pornstars)
        # pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
        # lista = item.contentTitle.split()
        # if "HD" in item.title:
            # lista.insert (4, pornstar)
        # else:
            # lista.insert (2, pornstar)
        # item.contentTitle = ' '.join(lista)
    if soup.find('div', class_='responsive-player').find(re.compile("(?:iframe|source)")):
        url = soup.find('div', class_='responsive-player').find(re.compile("(?:iframe|source)"))['src']
        if "php?q=" in url:
            import base64
            url = url.split('php?q=')
            url_decode = base64.b64decode(url[-1]).decode("utf8")
            url = urlparse.unquote(url_decode)
            url = scrapertools.find_single_match(url, '<(?:iframe|source) src="([^"]+)"')
    else:
        url = item.url
    itemlist.append(['[daftsex] .mp4', url])
    return itemlist
