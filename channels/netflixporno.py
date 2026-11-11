# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from platformcode import config, logger, unify
from core import scrapertools
from core import servertools
from core.item import Item
from core import httptools
from core import urlparse
from modules import autoplay
from bs4 import BeautifulSoup
from core import jsontools as json


UNIFY_PRESET = config.get_setting("preset_style", default="Inicial")
color = unify.colors_file[UNIFY_PRESET]

list_quality = ['default']
list_servers = ['mangovideo']

#  https://mangoporn.net   
#  https://pandamovies.pw/ & https://xxxparodyhd.net & https://streamporn.pw/ & https://streamporn.li 
#  https://www.netflixporno.net & https://watchpornfree.info & https://losporn.org/ 
#  https://xxxscenes.net & https://watchfreexxx.net/ & https://speedporn.net &https://pornkino.cc/
#  https://pornmovieshd.com/
#  https://watchpornx.com/


canonical = {
             'channel': 'netflixporno', 
             'host': config.get_setting("current_host", 'netflixporno', default=''), 
             'host_alt': ["https://watchpornx.com/"], 
             'host_black_list': ["https://netflixporno.net/", "https://streamporn.li"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
timeout = 10


def mainlist(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Ultimas", action="lista", url=host + "page/1?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas", action="lista", url=host + "page/1?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mejor Valorada", action="lista", url=host + "page/1?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas Larga", action="lista", url=host + "page/1?filter=longest"))
    
    itemlist.append(Item(channel=item.channel, title="Year", action="catalogo", url=host + "porn-years"))
    itemlist.append(Item(channel=item.channel, title="Canal", action="catalogo", url=host + "studios?sort=pop"))
    itemlist.append(Item(channel=item.channel, title="Pornstar", action="catalogo", url=host + "pornstars?sort=pop"))
    itemlist.append(Item(channel=item.channel, title="Categorias", action="categorias", url=host + "porn-genres"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host))
    # itemlist.append(Item(channel=item.channel, title="-------------------"))
    # itemlist.append(Item(channel=item.channel, title="Escenas", action="submenu", url=host + "xxxscenes/"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Ultimos", action="lista", url=item.url + "movies"))
    itemlist.append(Item(channel=item.channel, title="Canal", action="categorias", url=item.url , id="menu-item-38820"))
    itemlist.append(Item(channel=item.channel, title="Categorias", action="categorias", url=item.url,  id="menu-item-38760"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?s=%s&filter=latest" % (item.url, texto)
    try:
        return lista(item)
    except Exception:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    
    soup = create_soup(item.url)
    matches = soup.find('div', class_='chips').find_all('a')
    
    for elem in matches:
        url = elem['href']
        
        title = elem.text.strip()
        if elem.small:
            cantidad = elem.small.text.strip()
            title = title.replace(cantidad, '')
            title = "%s (%s)" %(title, cantidad)
        
        plot = ""
        thumbnail = ""
        if elem.img:
            thumbnail = elem.img.get('src', '')
        if not url.startswith("https"):
            url = "https:%s" % url
        if "#" not in url:
            itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                                 thumbnail=thumbnail, plot=plot))
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url, next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    
    soup = create_soup(item.url)
    matches = soup.find('div', class_='tgrid').find_all('a')
    
    for elem in matches:
        url = elem['href']
        
        title = elem.b.text.strip()
        if elem.small:
            cantidad = elem.small.text.strip()
            title = "%s (%s)" %(title, cantidad)
        
        plot = ""
        thumbnail = ""
        if elem.img:
            thumbnail = elem.img.get('src', '')
        if not url.startswith("https"):
            url = "https:%s" % url
        if "#" not in url:
            itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                                 thumbnail=thumbnail, plot=plot))
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url, next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    
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
    matches = soup.find_all('article', class_='card')
    for elem in matches:
        year = ""
        url = elem.a['href']
        title = elem.h2.text.strip()
        thumbnail = elem.img['src']
        if "svg" in thumbnail:
            thumbnail = elem.img['data-lazy-src']
        if "xxxscenes" not in item.url:
            year = elem.find('span', class_='card__q')
            if year:
                year = year.text.strip()
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                             fanart=thumbnail, contentTitle=title, infoLabels={"year": year} ))
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url, next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    video_urls = []
    soup = create_soup(item.url)
    pornstars = soup.find_all('a', href=re.compile("/(?:actor|pornstar|cast)/"))
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    if "N/A" not in pornstar:
        pornstar = "[COLOR %s]%s[/COLOR]" % (color.get('rating_3',''), pornstar)
    else:
        pornstar = ""
    plot = pornstar
    # lista = item.contentTitle.split()
    # lista.insert (0, pornstar)
    # item.contentTitle = ' '.join(lista)
    
    data = soup.section['data-servers']
    JSONData = json.load(data)
    
    for elem in JSONData:
        url = elem['u']
        itemlist.append(Item(channel=item.channel, title='%s', url=url, action='play', plot=plot, language='VO',contentTitle = item.contentTitle))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server)
    
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    
    return itemlist
