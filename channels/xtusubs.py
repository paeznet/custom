# -*- coding: utf-8 -*-
# -*- Channel xtusubs -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup


canonical = {
             'channel': 'xtusubs', 
             'host': config.get_setting("current_host", 'xtusubs', default=''), 
             'host_alt': ["https://xtusubs.com/"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s*rel="?stylesheet"?'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host ))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ss?search=%s" % (host,texto)
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
    matches = soup.find_all('a', class_='cora')
    for elem in matches:
        url = elem['href']
        title = elem.text.strip()
        url = urlparse.urljoin(item.url,url)
        
        thumbnail = ""
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
    matches = soup.find_all('a', class_='video')
    for elem in matches:
        url = elem['href']
        premium = ""
        if "suscript" in url:
            premium = "[COLOR gold]PREMIUM[/COLOR] "
        titulo =  elem['title']
        title = "%s%s" %(premium, titulo)
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-original']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        thumbnail = urlparse.urljoin(host, thumbnail)
        time = elem.find('span', class_='geirt').text.strip()
        quality = elem.find('span', class_='dimg')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (time, quality.text.strip(),title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(host, url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('section')
    if next_page:
        next_page = next_page.find_all('a')[-1]['href']
        next_page = urlparse.urljoin(host, next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    
    
    # https://xtusubs.com/s?onliwatch=2181&load=2695a5a90958690
    # https://xtusubs.com/iframe.php?onliview=873a71b7b291c + &gest&nulled
                                                          # + &netu&nulled
    ##### NETIU NO TIENE
    # soup = create_soup(item.url)
    # url = soup.iframe['src']
    # url = urlparse.urljoin(item.url, url)
    # matches = create_soup(url).find_all('a', class_='bold')
    # for elem in matches:
        # url = elem['href']
    # url += "&gest&nulled"
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist



def play(item):
    logger.info()
    itemlist = []
    
    # soup = create_soup(item.url)
    # pornstars = soup.find_all('a', href=re.compile("/models/[A-z0-9-]+/"))
    # for x , value in enumerate(pornstars):
        # pornstars[x] = value.text.strip()
    # pornstar = ' & '.join(pornstars)
    # pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    # lista = item.contentTitle.split()
    # if "HD" in item.title:
        # lista.insert (4, pornstar)
    # else:
        # lista.insert (2, pornstar)
    # item.contentTitle = ' '.join(lista)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
