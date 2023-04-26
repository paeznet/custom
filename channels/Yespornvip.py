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
import xbmc
import xbmcgui

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup
canonical = {
             'channel': 'Yespornvip', 
             'host': config.get_setting("current_host", 'Yespornvip', default=''), 
             'host_alt': ["https://yesporn.vip/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="canal", url=host + "actors/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="canal", url=host + "categories-2/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "tags-2/" ))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?s=%s&filter=latest" % (host,texto)
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
    matches = soup.main.find_all('a', href=re.compile(r"/tag/"))
    for elem in matches:
        url = elem['href']
        title = elem.text.strip()
        url += "?filter=latest"
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return itemlist


def canal(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_='videos-list').find_all('article', class_=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-src']
        url += "?filter=latest"
        plot = ""
        if not "tag" in url:
            itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                                 fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='current')
    if next_page and next_page.parent.find_next_sibling("li"):
        next_page = next_page.parent.find_next_sibling("li").a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="canal", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    matches = soup.main.find_all('article', class_=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        if "PRIVACY POLICY" in title:
            continue
        thumbnail = elem.img['data-src']
        if "base64" in thumbnail:
            thumbnail = elem.img['src']
        time = elem.find('span', class_='duration').text.strip()
        quality = elem.find('span', class_='hd-video')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        pornstars = elem['class']
        patron = 'actors-([A-z0-9-]+)'
        pornstars = re.compile(patron,re.DOTALL).findall(str(elem))
        for x , value in enumerate(pornstars):
            pornstars[x] = value.replace("-", " ")
        pornstar = '\n'.join(pornstars)
        plot = "[COLOR cyan]%s[/COLOR]" % pornstar
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
    matches = soup.find_all('div', class_='responsive-player')
    if soup.find('div', class_='iframe-container'):
        matches.append(soup.find('div', class_='iframe-container'))
    for elem in matches:
        url = elem.iframe['data-src']
        if "player-x.php?" in url:
            url = url.split("q=")
            url = url[-1]
            import sys, base64
            url = base64.b64decode(url).decode('utf8')
            url = urlparse.unquote(url)
            url = BeautifulSoup(url, "html5lib", from_encoding="utf-8")
            url = url.source['src']
        itemlist.append(Item(channel=item.channel, action="play", contentTitle = item.contentTitle, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='responsive-player')
    if soup.find('div', class_='iframe-container'):
        matches.append(soup.find('div', class_='iframe-container'))
    for elem in matches:
        url = elem.iframe['data-src']
        if "player-x.php?" in url:
            url = url.split("q=")
            url = url[-1]
            import sys, base64
            url = base64.b64decode(url).decode('utf8')
            url = urlparse.unquote(url)
            url = BeautifulSoup(url, "html5lib", from_encoding="utf-8")
            url = url.source['src']
        itemlist.append(Item(channel=item.channel, action="play", contentTitle = item.contentTitle, url=url))
    return itemlist
