# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from core import jsontools
from bs4 import BeautifulSoup

canonical = {
             'channel': 'tube8', 
             'host': config.get_setting("current_host", 'tube8', default=''), 
             'host_alt': ["https://www.tube8.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "newest.html"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "mostviewed.html"))
    itemlist.append(Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "mostfavorited.html"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "top.html"))
    itemlist.append(Item(channel=item.channel, title="Mas metraje" , action="lista", url=host + "longest.html"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="catalogo", url=host + "pornstars/?sort=rl"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "top-channels/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories.html"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearches.html?q=%s&orderby=newest" % (host,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    if "channels" in item.url:
        matches = soup.find_all('div', class_='channel_box')
    else:
        matches = soup.find('div', class_='popularPornstars-wrapper').find_all('div', class_='porn-star-list')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        if elem.img.get('data-src', ''):
            thumbnail = elem.img['data-src']
        else:
            thumbnail = elem.img['src']
        cantidad = elem.find(class_=re.compile("video(:?-|_)count"))
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('div', id='next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_='categoriesList').find_all('a')
    for elem in matches:
        url = elem['href']
        cantidad = elem.find('div', class_='videos')
        title = elem.img['alt']
        cantidad = elem.find('span')
        thumbnail = elem.img['data-src']
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url, url)
        url += "?orderby=nt"
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                            fanart=thumbnail, thumbnail=thumbnail) )
    if "categories" in item.url:
        itemlist.sort(key=lambda x: x.title)
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
        data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)#.find('div', id='category_video_list')
    matches = soup.find_all('div', class_='video-box')
    for elem in matches:
        if elem.ins: continue
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['data-src']
        quality = elem.find('p', class_='video-best-resolution')
        time = elem.find(class_='video-duration').text.strip()
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (time, quality.text.strip(), title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url, url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        else:
            itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, contentTitle=title,
                                 fanart=thumbnail, thumbnail=thumbnail, plot=plot))
    next_page = soup.find('div', id='next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    if soup.find('div',id='metaDataPornstarInfo'):
        # pornstars = soup.find('div',id='metaDataPornstarInfo').find_all('a', href=re.compile("/pornstar/"))
        pornstars = soup.find('div',id='metaDataPornstarInfo').find_all('a', class_='metaDataPornstarLink')
        for x , value in enumerate(pornstars):
            pornstars[x] = value.text.strip()
        pornstar = ' & '.join(pornstars)
        pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
        lista = item.contentTitle.split()
        if "[COLOR red]" in item.title:
            lista.insert (4, pornstar)
        else:
            lista.insert (2, pornstar)
        item.contentTitle = ' '.join(lista)    
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
