# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger, platformtools, unify
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup

UNIFY_PRESET = config.get_setting("preset_style", default="Inicial")
color = unify.colors_file[UNIFY_PRESET]

IDIOMAS = {}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_servers = []
forced_proxy_opt = 'ProxySSL'

# https://www.xvideospanish.net  https://www.xn--xvideos-espaol-1nb.com/
canonical = {
             'channel': 'xvideospanish', 
             'host': config.get_setting("current_host", 'xvideospanish', default=''), 
             'host_alt': ["https://www.xn--xvideos-espaol-1nb.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas longitud" , action="lista", url=host + "?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "actors/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "videos-pornos-por-productora-gratis/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?s=%s" % (host,texto)
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
    matches = soup.find('div', class_='videos-list').find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        url = url.replace("https://www.xvideos-español.com" , host)
        thumbnail = thumbnail.replace("https://www.xvideos-español.com" , host)
        url
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, thumbnail=thumbnail,
                                  fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='current')
    if next_page:
        next_page = next_page.parent.find_next_sibling("li").a['href']
        next_page = next_page.replace("https://www.xvideos-español.com" , host)
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    matches = soup.find('main', id='main').find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        if elem.img:
            thumbnail = elem.img['src']
            if ".gif" in thumbnail:
                thumbnail = elem.img['data-src']
        else:
            thumbnail = elem.video['poster']
        time = elem.find('span', class_='duration')
        if time:
            time = time.text.strip()
            title = "[COLOR %s]%s[/COLOR] %s" % (color.get('year',''), time,title)
        url = url.replace("https://www.xvideos-español.com" , host)
        thumbnail = thumbnail.replace("https://www.xvideos-español.com" , host)
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                                  fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='current')
    if next_page:
        next_page = next_page.parent.find_next_sibling("li").a['href']
        next_page = next_page.replace("https://www.xvideos-español.com" , host)
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    url = create_soup(item.url).find('meta', itemprop='embedURL')['content']
    if url:
        itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    
    soup = create_soup(item.url)
    pornstars = soup.find('div', class_='video-tags').find_all('a', href=re.compile("/actor/[A-z0-9-]+/"))
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR %s]%s[/COLOR]" % (color.get('rating_3',''), pornstar)
    lista = item.contentTitle.split()
    if "HD" in item.title:
        lista.insert (4, pornstar)
    else:
        lista.insert (2, pornstar)
    item.contentTitle = ' '.join(lista)
    
    
    url = soup.find('meta', itemprop='embedURL')['content']
    if "dato.porn" in url or "datoporn" in url or "openload" in url or "videomega." in url:
        url = ""
    if url:
        itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    else:
        platformtools.dialog_ok("xvideospanish: Error", "El archivo no existe o ha sido borrado")
        return
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist