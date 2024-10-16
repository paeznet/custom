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

#   https://www.peekvids.com/     https://www.playvids.com/

canonical = {
             'channel': 'playvids', 
             'host': config.get_setting("current_host", 'playvids', default=''), 
             'host_alt': ["https://www.playvids.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': True, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "?page=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "Trending-Porn"))
    itemlist.append(Item(channel=item.channel, title="Pornstar" , action="pornstars", url=host + "pornstars?page=1"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "channels"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%svideos?q=%s" % (host,texto)
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
    soup = create_soup(item.url).find('div', class_='category-list-view').parent
    matches = soup.find_all('li')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text.strip()
        cantidad = elem.find('span')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        url += "?page=1"
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='card')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        cantidad = elem.find('span', class_='amount-videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        url += "/?page=1"
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def pornstars(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('ul', class_='stars_list').find_all('li')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text.strip()
        thumbnail = ""
        if elem.a.get('title', ''):
            thumbnail = elem.a['title']
            thumbnail = scrapertools.find_single_match(thumbnail, "src='([^']+)'" )
        # cantidad = elem.find('span')
        # if cantidad:
            # title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        url += "?page=1"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="pornstars", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    # matches = soup.find_all('div', class_=re.compile(r"^video-item-\d+"))
    matches = soup.find_all('div', class_='itemVideo')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        time = elem.find('span', class_='duration').text.strip()
        quality = elem.find('span', class_='hd')
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
    if soup.find('button', class_='auto_more'):
        current_page = soup.find('button', class_='auto_more')['data-page']
        next_page = int(current_page) + 1
        next_page = re.sub(r"page=\d+", "page={0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    else:
        next_page = soup.find('a', class_='next')
        if next_page:
            next_page = next_page['href']
            next_page = urlparse.urljoin(item.url,next_page)
            itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron = 'data-hls-src(\d+)="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality, url in matches:
        url = url.replace("amp;", "")
        itemlist.append(Item(channel=item.channel, action="play", title= "%s" %quality, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    data = httptools.downloadpage(item.url, canonical=canonical).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    
    pornstars = soup.find('ul', class_='detail-video').find_all('a', href=re.compile("/pornstar/[A-z0-9-]+"))
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    lista = item.contentTitle.split()
    if "HD" in item.title:
        lista.insert (4, pornstar)
    else:
        lista.insert (2, pornstar)
    item.contentTitle = ' '.join(lista)
    
    
    patron = 'data-hls-src(\d+)="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality, url in matches:
        url = url.replace("amp;", "")
        itemlist.append(['[peekvids] %sp' %quality, url])
    return itemlist
