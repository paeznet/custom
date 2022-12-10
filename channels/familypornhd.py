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

canonical = {
             'channel': 'familypornhd', 
             'host': config.get_setting("current_host", 'familypornhd', default=''), 
             'host_alt': ["https://familypornhd.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "page/1/"))
    itemlist.append(Item(channel=item.channel, title="SISTER & BROTHER" , action="lista", url=host + "page/1/?filter-by=taxonomy&obj=post_tag&obj-id=71"))
    itemlist.append(Item(channel=item.channel, title="DAD & DAUGHTER" , action="lista", url=host + "page/1/?filter-by=taxonomy&obj=post_tag&obj-id=106"))
    itemlist.append(Item(channel=item.channel, title="SON & MOTHER" , action="lista", url=host + "page/1/?filter-by=taxonomy&obj=post_tag&obj-id=120"))
    # itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/pornstars/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "channels/"))

    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%spage/1/?s=%s" % (host,texto)
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
    matches = soup.find_all('div', class_='elementor-widget-container')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text.strip()
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('li', class_='g1-terms-item')
    for elem in matches:
        url = elem.a['href']
        title = elem.h4.text.strip()
        thumbnail = elem.a['style']
        thumbnail = scrapertools.find_single_match(thumbnail, "url\(([^\\)]+)")
        cantidad = elem.find('span', class_='g1-term-count')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
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
    matches = soup.find_all('article',class_='type-post')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        canal = elem.find('a', class_='entry-category')
        if canal:
            title = "[%s] %s" % (canal.text.strip(), title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    ref = soup.iframe['src']
    data = httptools.downloadpage(ref, headers={'Referer': item.url}).data
    videourl = scrapertools.find_single_match(data, '"videoUrl":"([^"]+)"').replace("\/", "/")
    videoserver = scrapertools.find_single_match(data, '"videoServer":"([^"]+)"')
    videourl = "%s?s=%s&d=" %(videourl,videoserver)
    videourl = urlparse.urljoin(ref,videourl)
    headers = {'Accept': '*/*', 'Referer': videourl}
    data = httptools.downloadpage(videourl, headers= headers).data
    patron = 'RESOLUTION=\d+x(\d+)\s*([^\s]+)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,url in matches:
        url += "|Referer=%s" %ref
        itemlist.append(Item(channel=item.channel, action="play", title= quality, contentTitle = item.title, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    ref = soup.iframe['src']
    pornstar = soup.find('p', class_='has-text-align-center').text.strip()
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar.replace("Pornstar: ", "")
    lista = item.contentTitle.split("]")
    lista[0]= "%s]" %lista[0]
    lista.insert (1, pornstar)
    item.contentTitle = ' '.join(lista)    
    data = httptools.downloadpage(ref, headers={'Referer': item.url}).data
    videourl = scrapertools.find_single_match(data, '"videoUrl":"([^"]+)"').replace("\/", "/")
    videoserver = scrapertools.find_single_match(data, '"videoServer":"([^"]+)"')
    videourl = "%s?s=%s&d=" %(videourl,videoserver)
    videourl = urlparse.urljoin(ref,videourl)
    headers = {'Accept': '*/*', 'Referer': videourl}
    data = httptools.downloadpage(videourl, headers= headers).data
    patron = 'RESOLUTION=\d+x(\d+)\s*([^\s]+)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,url in matches:
        url += "|Referer=%s" %ref
        itemlist.append(['%sp' %quality, url])
    itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return itemlist
