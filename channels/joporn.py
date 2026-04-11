# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger, platformtools
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup

forced_proxy_opt = 'ProxySSL'

# https://josporn.net/

canonical = {
             'channel': 'joporn', 
             'host': config.get_setting("current_host", 'joporn', default=''), 
             'host_alt': ["https://josporn.net/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=host + "search/?sort_by=post_date&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="list_all", url=host + "search/?sort_by=video_viewed_month&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor Valorada" , action="list_all", url=host + "search/?sort_by=rating_month&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Favoritas" , action="list_all", url=host + "search/?sort_by=most_favourited&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Comentadas" , action="list_all", url=host + "search/?sort_by=most_commented&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Largas" , action="list_all", url=host + "search/?sort_by=duration&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="categoria", url=host + "models/?sort_by=total_videos&from=1", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categoria", url=host + "categories/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search/?q=%s&sort_by=post_date&from_videos=1" % (host,texto)
    try:
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categoria(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_=re.compile("list-(?:categories|models)")).find_all('a', class_='item')
    for elem in matches:
        url = elem['href']
        title = elem['title']
        cantidad = ""
        if elem.find('div', class_='videos'):
            cantidad = elem.find('div', class_='videos').text.strip()
        if cantidad:
            title = "%s (%s)" %(title,cantidad)
        url = urlparse.urljoin(item.url,url)
        thumbnail = elem.img['src']
        plot = ""
        itemlist.append(item.clone(action="list_all", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='next')
    if next_page and next_page.find('a'):
        next_page = next_page.a['data-parameters'].split(":")[-1]
        if "from_videos" in item.url:
            next_page = re.sub(r"&from_videos=\d+", "&from_videos={0}".format(next_page), item.url)
        else:
            next_page = re.sub(r"&from=\d+", "&from={0}".format(next_page), item.url)
        itemlist.append(item.clone(action="categoria", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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



def list_all(item):
    logger.info()
    itemlist = []
    
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='item')
    for elem in matches:
        if elem.find('script'):
            continue
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src'].replace(r'336x189/\d+', 'preview')
        if 'base64' in thumbnail:
            thumbnail = elem.img['data-original'].replace(r'336x189/\d+', 'preview')
        
        time = elem.find('div', class_='duration').text.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(item.clone(action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('li', class_='next')
    if next_page and next_page.find('a'):
        next_page = next_page.a['data-parameters'].split(":")[-1]
        if "from_videos" in item.url:
            next_page = re.sub(r"&from_videos=\d+", "&from_videos={0}".format(next_page), item.url)
        else:
            next_page = re.sub(r"&from=\d+", "&from={0}".format(next_page), item.url)
        itemlist.append(item.clone(action="list_all", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    
    url = ""
    url = soup.find('a', class_='btn-play')
    if url and not 'josporn' in url['href']: 
        item.url = url['href']
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    
    pornstars = soup.find_all('a', href=re.compile("/models/[A-z0-9-]+/"))
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    lista = item.contentTitle.split()
    lista.insert (2, pornstar)
    item.contentTitle = ' '.join(lista)
    
    url = ""
    url = soup.find('a', class_='btn-play')
    if url and not 'josporn' in url['href']: 
        item.url = url['href']
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

