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

# https://mat6tube.com/   https://noodlemagazine.com/   https://ukdevilz.com/

##### cloudflare error 403
 ### thumbnail  CCurlFile::Stat - Failed: HTTP response code said error(22)


forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'mat6tube', 
             'host': config.get_setting("current_host", 'mat6tube', default=''), 
             'host_alt': ["https://mat6tube.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
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
    matches = soup.find_all('div', class_='item')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('div', class_='title').text.strip()
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
    next_page = soup.find_all('div', class_='more')
    if next_page:
        next_page = next_page[-1]['data-page']
        next_page = re.sub(r"&p=\d+", "&p={0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist

def findvideos(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data, '"embedUrl":\s*"([^"]+)"')
    data = httptools.downloadpage(url).data
    patron = '\{"file":\s*"([^"]+)".*?'
    patron += '"label":\s*"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url,quality in matches:
        # itemlist.append(['%s' %quality, url])
        itemlist.append(Item(channel=item.channel, action="play", title= "%s" %quality, contentTitle = item.title, url=url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data, '"embedUrl":\s*"([^"]+)"')
    data = httptools.downloadpage(url).data
    patron = '\{"file":\s*"([^"]+)".*?'
    patron += '"label":\s*"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url,quality in matches:
        itemlist.append(['%s' %quality, url])
    itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return itemlist

