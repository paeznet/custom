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

forced_proxy_opt = 'ProxySSL'
#  "https://bitporno.de" #"https://bitporno.to"  

# m3u8 El enlace no es un video (se encontro tipo text/html)

canonical = {
             'channel': 'bitporno', 
             'host': config.get_setting("current_host", 'bitporno', default=''), 
             'host_alt': ["https://www.bitporno.com/"], 
             'host_black_list': ["https://bitporno.to"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host + "/search/all/sort-recent/time-today/cat-/page-"))
    itemlist.append(item.clone(title="Mas vistos" , action="lista", url=host + "/search/all/sort-mostviewed/time-today/cat-/page-"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?q=%s" % (host,texto)
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
    soup = create_soup(item.url).find('span', string='Categories')
    matches = soup.find_next_sibling('div').find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.text
        url = urlparse.urljoin(item.url,url)
        thumbnail = ""
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              thumbnail=thumbnail) )
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
    matches = soup.find_all('div', class_='entry')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('div')
        if "HD" in title.text:
            title = title.find_next_sibling('div')
        title = title.text
        thumbnail = elem.img['src']
        quality = elem.find('div', class_='thumbnail-hd')
        if quality and title:
            title = "[COLOR red]HD[/COLOR] %s" % title
        url = urlparse.urljoin(item.url,url)
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        if title:
            itemlist.append(item.clone(action=action, title=title, url=url, thumbnail=thumbnail,
                                fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='pages-active')
    if next_page:
        next_page = next_page.find_next('a')['href']
        next_page = urlparse.urljoin(host,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    # url = scrapertools.find_single_match(data, 'file: "([^"]+)"')
    url = scrapertools.find_single_match(data, "url: '([^']+)'")
    if ".m3u" in url:
        url= urlparse.urljoin(host,url)
        m3u_data = httptools.downloadpage(url).data
        matches = scrapertools.find_multiple_matches(m3u_data, 'TION=\d+x(\d+).*?\s(.*?)\s')
        filename = scrapertools.get_filename_from_url(url)[-4:]
        if matches:
            for quality, url in matches:
                itemlist.append(["%s  %sp [bitporno]" % (filename, quality), url])
    else:
        itemlist.append(["[bitporno] .mp4", url])
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    # url = scrapertools.find_single_match(data, 'file: "([^"]+)"')
    url = scrapertools.find_single_match(data, "url: '([^']+)'")
    if ".m3u" in url:
        url= urlparse.urljoin(host,url)
        m3u_data = httptools.downloadpage(url).data
        matches = scrapertools.find_multiple_matches(m3u_data, 'TION=\d+x(\d+).*?\s(.*?)\s')
        filename = scrapertools.get_filename_from_url(url)[-4:]
        if matches:
            for quality, url in matches:
                itemlist.append(["%s  %sp [bitporno]" % (filename, quality), url])
    elif url:
        itemlist.append(["[bitporno] .mp4", url])
    return itemlist

