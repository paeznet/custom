# -*- coding: utf-8 -*-
# -*- Channel CzechVideo -*-
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

############   NETU

canonical = {
             'channel': 'czechvideo', 
             'host': config.get_setting("current_host", 'czechvideo', default=''), 
             'host_alt': ["https://czechvideo.ac/"], 
             'host_black_list': [], 
             'pattern': ['<link rel="preconnect" href="([^"]+"'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

api = "lastnews/page/1/?dlenewssortby=%s&dledirection=desc&set_new_sort=dle_sort_lastnews&set_direction_sort=dle_direction_lastnews"

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url= host + api %"date"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url= host + api %"rate"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


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
    matches = soup.find('div', class_='cat').find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.text.strip()
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
    matches = soup.find_all('div', class_='short-story')
    
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-src']
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        if elem.find('div', class_='short-time'):
            time = elem.find('div', class_='short-time').text.strip()
        quality = elem.find('span', class_='is-hd')
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
    next_page = soup.find('div', class_='navigation').find_all('a')[-1]
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



def play(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(item.url, canonical=canonical).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    
    patron = "<p>Featuring:\s*</p>\s*([^<]+)"
    pornstars = scrapertools.find_single_match(data, patron).strip()
    pornstars = pornstars.replace(' aka ', ' , ')
    if ", " in pornstars:
        pornstars = pornstars.split(", ")
        for elem in pornstars:
            if elem in item.contentTitle:
                item.contentTitle = item.contentTitle.replace(elem, "[COLOR cyan]%s[/COLOR]" % elem)
        item.contentTitle = item.contentTitle.replace("[/COLOR] and [COLOR cyan]", " and ").replace("[/COLOR]and [COLOR cyan]", " and ")
    elif pornstars:
        if pornstars in item.contentTitle:
            item.contentTitle = item.contentTitle.replace(pornstars, "[COLOR cyan]%s[/COLOR]" % pornstars)
            item.contentTitle = item.contentTitle.replace("[/COLOR] and [COLOR cyan]", " and ").replace("[/COLOR]and [COLOR cyan]", " and ")
    # pornstar = pornstars.replace(", ", "&")
    # pornstar = "[COLOR cyan]%s" % pornstar
    # lista = item.contentTitle.split("[/COLOR]")
    # lista.insert (1, pornstar)
    # item.contentTitle = '[/COLOR] '.join(lista)
    
    url = soup.find('iframe', class_='netu')
    if soup.find('iframe', class_='netu'):
        url = soup.find('iframe', class_='netu')['src']
        if "=" in url: 
            id = url.split("=")[-1]
            url = "https://hqq.to/e/%s" %id
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
