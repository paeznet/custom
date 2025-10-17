# -*- coding: utf-8 -*-
# -*- Channel youperv -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import re

from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup


canonical = {
             'channel': 'youperv', 
             'host': config.get_setting("current_host", 'youperv', default=''), 
             'host_alt': ["https://youperv.com/"], 
             'host_black_list': [], 
             'pattern': ['<link rel="preconnect" href="([^"]+"'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

api = "page/1/?dlenewssortby=%s&dledirection=desc&set_new_sort=dle_sort_main&set_direction_sort=dle_direction_main"

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url= host + api %"date"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url= host + api %"rating"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist

# https://youperv.com/index.php?do=search&subaction=search&search_start=2&full_search=0&story=big

def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%sindex.php?do=search&subaction=search&full_search=0&story=%s&search_start=1" % (host,texto)
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
    matches = soup.find_all('span', class_=re.compile(r"^clouds_[a-z]+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text.strip()
        thumbnail = ""
        url = urlparse.urljoin(item.url,url)
        url += "page/1/"
        # thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
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
    matches = soup.find_all('div', class_='item')
    
    for elem in matches:
        url = elem.a['href']
        title = elem.img['title']
        thumbnail = elem.img['src']
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        if elem.find('span', class_='tim'):
            time = elem.find('span', class_='tim').text.strip()
        quality = elem.find('div', class_='item-meta')
        if elem.find('a', href=re.compile("/pornstar/[A-z0-9-%20]+(?:/|)")):
            pornstars = elem.find_all('a', href=re.compile("/pornstar/[A-z0-9-%20]+(?:/|)"))
            if pornstars:
                for x, value in enumerate(pornstars):
                    pornstars[x] = value.get_text(strip=True)
                pornstar = ' & '.join(pornstars)
            title = "[COLOR cyan]%s[/COLOR] %s" %(pornstar, title)
        
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('div', class_='pagi-nav').find_all('a')[-1]
    if next_page:
        if next_page.get('onclick',''):
            next_page = scrapertools.find_single_match(next_page['onclick'], "(\d+)")
            next_page = re.sub(r"&search_start=\d+", "&search_start={0}".format(next_page), item.url)
        else:
            next_page = next_page['href'].split("/page/")[-1]
            next_page = re.sub(r"/page/\d+/", "/page/{0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


