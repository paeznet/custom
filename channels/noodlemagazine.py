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

# https://mat6tube.com/   https://noodlemagazine.com/

 ### thumbnail  CCurlFile::Stat - Failed: HTTP response code said error(22)

canonical = {
             'channel': 'noodlemagazine', 
             'host': config.get_setting("current_host", 'noodlemagazine', default=''), 
             'host_alt': ["https://noodlemagazine.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Buscar Nuevos" , action="search", ver=0))
    # itemlist.append(Item(channel=item.channel, title="Buscar Mas vistos" , action="search", ver=3))
    itemlist.append(Item(channel=item.channel, title="Buscar Mejor valorados" , action="search", ver=2))
    itemlist.append(Item(channel=item.channel, title="Buscar Mas largos" , action="search", ver=1))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%svideo/%s?sort=%s&p=0" % (host, texto, item.ver)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


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
    matches = soup.find_all('div', class_="item")
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['data-src']  ### CCurlFile::Stat - Failed: HTTP response code said error(22)
        # thumbnail += "|verifypeer=false"
        # thumbnail += "|ignore_response_code=True"
        # thumbnail += "|Referer=%s" % host
        time = elem.find('div', class_='m_time').text.strip()
        quality = elem.find('i', class_='hd_mark')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                                   plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('div', class_='more')
    if next_page:
        current_page = scrapertools.find_single_match(item.url, ".*?=(\d+)")
        page = scrapertools.find_single_match(item.url, "(.*?)=\d+")
        current_page = int(current_page)
        current_page += 1
        next_page = "%s=%s" % (page, current_page)
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    url = create_soup(item.url).find('iframe', id='iplayer')['src']
    url = urlparse.urljoin(item.url,url)
    data = httptools.downloadpage(url).data
    url = scrapertools.find_single_match(data, "window.playlistUrl='([^']+)'")
    url = urlparse.urljoin(item.url,url)
    data = httptools.downloadpage(url).json
    for elem in data['sources']:
        url = elem['file']
        url += "|Referer=%s" % host
        quality = elem['label']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    url = create_soup(item.url).find('iframe', id='iplayer')['src']
    url = urlparse.urljoin(item.url,url)
    data = httptools.downloadpage(url).data
    url = scrapertools.find_single_match(data, "window.playlistUrl='([^']+)'")
    url = urlparse.urljoin(item.url,url)
    data = httptools.downloadpage(url).json
    for elem in data['sources']:
        url = elem['file']
        url += "|Referer=%s" % host
        quality = elem['label']
        itemlist.append(['%sp [.mp4]' %quality, url])
    itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return itemlist
