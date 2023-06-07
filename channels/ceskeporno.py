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

# https://ceskeporno.cz  https://ceske-kundy.cz/   https://porno-videa-zdarma.cz/
canonical = {
             'channel': 'ceskeporno', 
             'host': config.get_setting("current_host", 'ceskeporno', default=''), 
             'host_alt': ["https://porno-videa-zdarma.cz/"], 
             'host_black_list': [], 
             'pattern': ["BASE_URL = '([^']+)'"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

# NECESITA ASSISTANT CLOUDFLARE Cloudflare version 2

def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host + "?serazeni=nejnovejsi&obdobi=cela-doba&strana=1"))
    itemlist.append(item.clone(title="Mas vistos" , action="lista", url=host + "?serazeni=nejvice-shlednuti&obdobi=mesic&strana=1"))
    itemlist.append(item.clone(title="Mas largo" , action="lista", url=host + "?serazeni=nejdelsi&obdobi=mesic&strana=1"))
    itemlist.append(item.clone(title="PornStar" , action="categorias", url=host + "pornoherecky"))

    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "kategorie"))
    # itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ssearch/%s/" % (host,texto)
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
    matches = soup.find_all('div', class_='content')
    for elem in matches:
        url = elem.a['href']
        title = elem.h2.text.strip()
        thumbnail = elem.find('div')['style']
        cantidad = elem.span
        if cantidad:
            cantidad = cantidad.text.strip().replace(" videí", "")
            title = "%s (%s)" % (title,cantidad)
        thumbnail = thumbnail.replace("background-image: url(", "").replace(");", "").replace("'", "").replace("\"", "")
        thumbnail = urlparse.urljoin(host,thumbnail)
        plot = ""
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='item-pagin is_last')
    if next_page:
        next_page = next_page.a['data-parameters'].replace(":", "=").split(";").replace("+from_albums", "")
        next_page = "?%s&%s" % (next_page[0], next_page[1])
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    matches = soup.find_all('div', class_='content')
    for elem in matches:
        url = elem.a['data-url']
        title = elem.h2.text.strip()
        thumbnail = elem.find('div', class_='img')['data-srcset']
        time = elem.find('div', class_='duration').text.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(item.clone(action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('div', class_='pagination').find('a', class_='background-color')
    if next_page and next_page.parent.find_next_sibling("li"):
        next_page = next_page.parent.find_next_sibling("li").a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('source',  type='video/mp4')
    for elem in matches:
        url = elem['src']
        url = urlparse.urljoin(item.url,url)
        quality = elem['title']
        itemlist.append(['.mp4 %s' %quality, url])
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('source',  type='video/mp4')
    for elem in matches:
        url = elem['src']
        url = urlparse.urljoin(item.url,url)
        quality = elem['title']
        itemlist.append(['.mp4 %s' %quality, url])
    return itemlist[::-1]
