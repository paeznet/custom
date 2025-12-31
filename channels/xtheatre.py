# -*- coding: utf-8 -*-
#------------------------------------------------------------
import re

from platformcode import config, logger
from core import scrapertools
from core import servertools
from core.item import Item
from core import httptools
from core import urlparse
from bs4 import BeautifulSoup
from modules import autoplay
from lib.alfa_assistant import is_alfa_installed

forced_proxy_opt = 'ProxySSL'


IDIOMAS = {'vo': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['vidlox']

####          Just a moment...     FUNCIONA CON WARP
# cf_assistant = "force" if is_alfa_installed() else False
cf_assistant = True if is_alfa_installed() else False
forced_proxy_opt = None if cf_assistant else 'ProxySSL'
cf_debug = True

timeout = 15

canonical = {
             'channel': 'xtheatre', 
             'host': config.get_setting("current_host", 'xtheatre', default=''), 
             'host_alt': ["https://pornxtheatre.com/"], 
             'host_black_list': [], 
             # 'set_tls': None, 'set_tls_min': False, 'retries_cloudflare': 7, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             # 'cf_assistant': False, 'CF_stat': True, 
             # 'CF': False, 'CF_test': False, 'alfa_s': True
             
             # 'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             # 'CF': False, 'CF_test': False, 'alfa_s': True
             
             'set_tls': True, 'set_tls_min': True, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': cf_assistant, 
             'cf_assistant_ua': True, 'cf_assistant_get_source': True if cf_assistant == 'force' else False, 
             'cf_no_blacklist': True, 'cf_removeAllCookies': False if cf_assistant == 'force' else True,
             'cf_challenge': True, 'cf_returnkey': 'url', 'cf_partial': True, 'cf_debug': cf_debug, 
             'cf_cookies_names': {'cf_clearance': False},
             'CF_if_assistant': True if cf_assistant is True else False, 'retries_cloudflare': -1, 
             'CF_stat': True if cf_assistant is True else False, 'session_verify': True, 
             'CF': False, 'CF_test': False, 'alfa_s': True, 'renumbertools': False
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host + "?filter=latest"))
    itemlist.append(item.clone(title="Mas vistos" , action="lista", url=host + "?filter=most-viewed"))
    itemlist.append(item.clone(title="Mas largo" , action="lista", url=host + "?filter=longest"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "categories/"))
    itemlist.append(item.clone(title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?s=%s&filter=latest" % (host, texto)
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
    matches = soup.find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        if elem.img.get('src', ''):
            thumbnail = elem.img['src']
        else:
            thumbnail = elem.img['data-src']
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='current')
    if next_page and next_page.parent.find_next_sibling("li"):
        next_page = next_page.parent.find_next_sibling("li").a['href']
        itemlist.append(Item(channel = item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, timeout=timeout, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, timeout=timeout, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        if elem.img and elem.img.get('src', ''):
            thumbnail = elem.img['src']
        elif elem.img and "svg" in thumbnail:
            thumbnail = elem.img['data-lazy-src']
        else: 
            thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find("a", string=re.compile(r"^Next"))
    if next_page:
        next_page = next_page['href']
        next_page =  urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    frames = []
    soup = create_soup(item.url).find('div', class_='responsive-player')
    matches = soup.find_all('iframe')
    for elem in matches:
        url = elem['src']
        if "about:" in url:
            url =  elem['data-lazy-src']
        if not url in frames:
            frames.append(url)
            itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    autoplay.start(itemlist, item)
    return itemlist
