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
             'channel': 'xmax', 
             'host': config.get_setting("current_host", 'xmax', default=''), 
             'host_alt': ["https://xmax.to"], 
             'host_black_list': [], 
             'pattern': ['class="tidymag-site-title"><a href="?([^"|\s*]+)["|\s*]'], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host))
    # itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/popular/today/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
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
    matches = soup.find('div', class_='tagcloud').find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem['aria-label']
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
    soup = create_soup(item.url)
    matches = soup.find_all('div', id=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        if "rls1" in url:
            url = elem.a['real']
        title = elem.a['title'].replace("Permanent Link to ", "")
        thumbnail = elem.img['src']
        time = elem.find('i', class_='fa-clock-o').parent.text.strip()
        quality = elem.find('i', class_='fa-video-camera')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (time,quality.parent.text.strip(),title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='nextpostslink')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = "src:\s*'([^']+)', type: 'video/mp4', size: (\d+)"
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, quality in matches:
        itemlist.append(Item(channel=item.channel, action="play", title= quality, contentTitle = item.contentTitle, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = "src:\s*'([^']+)', type: 'video/mp4', size: (\d+)"
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, quality in matches:
        itemlist.append(['.mp4 %sp' %quality, url])
    return itemlist
