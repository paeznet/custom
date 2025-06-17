# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup

###    no muestra thumbnail    https://cdn.pervclips.com/tube/contents/videos_screenshots/1064102000/1064102366/367x275/3.jpg

canonical = {
             'channel': 'pervclips', 
             'host': config.get_setting("current_host", 'pervclips', default=''), 
             'host_alt': ["https://www.pervclips.com/"], 
             'host_black_list': [], 
             'pattern': ['class="?eng"?\s*href="?([^"|\s*]+)["|\s*]'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "tube/latest-updates/"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "tube/most-popular/month/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "tube/top-rated/month/"))
    itemlist.append(Item(channel=item.channel, title="Pornstar" , action="categorias", url=host + "tube/pornstars/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "tube/categories/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%stube/search/latest/?q=%s" % (host,texto)
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
    soup = create_soup(item.url).find('div', class_='new_cat')
    matches = soup.find_all('div', class_='item')
    for elem in matches:
        url = elem.a['href']
        if elem.find('p', class_='title'):
            title = elem.find('p', class_='title').text.strip()
        else:
            title = elem.img['alt']
        thumbnail = elem.img['src']
        cantidad = elem.find('span', class_='quantity')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
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
    matches = soup.find_all('div', class_='desktop-thumb')
    for elem in matches:
        url = elem.a['href']
        # title = elem.find('p', class_='title').text.strip()
        title = elem.img['alt']
        thumbnail = elem.img['data-original']
        thumbnail = thumbnail.replace("?ver=3", "")
        # logger.debug(thumbnail)
        # thumbnail += "|ignore_response_code=True"
        # thumbnail += "|Referer=%s" % host
        # thumbnail += "|verifypeer=false"
       
        time = elem.find('div', class_='time-holder').text.strip()
        quality = elem.find('i', class_='icon-hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        # thumbnail += "|Referer=%s" % host
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
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

def play(item):
    logger.info()
    itemlist = []
    
    soup = create_soup(item.url)
    if soup.find('div', class_='models'):
        pornstars = soup.find('div', class_='models').find_all('a', href=re.compile("/pornstars/[A-z0-9-]+/"))
        for x , value in enumerate(pornstars):
            pornstars[x] = value.text.strip()
        pornstar = ' & '.join(pornstars)
        pornstar = " [COLOR cyan]%s" % pornstar
        lista = item.contentTitle.split('[/COLOR]')
        if "[COLOR yellow]" in item.contentTitle:
            lista.insert (1, pornstar)
        else:
            lista.insert (0, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
