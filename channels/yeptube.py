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

canonical = {
             'channel': 'yeptube', 
             'host': config.get_setting("current_host", 'yeptube', default=''), 
             'host_alt': ["https://www.yeptube.com/"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s*rel="?stylesheet"?'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

# cookie lang=en; index_filter_sort=addtime
def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host, ctype="addtime", cattype = "straight"))
    # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host, ctype="rating_month", cattype = "straight"))
    # itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host, ctype="comments_month", cattype = "straight"))
    # itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host, ctype="longest", cattype = "straight"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", ctype="addtime", cattype = "straight"))

    # itemlist.append(Item(channel=item.channel, title="", action="", folder=False))

    # itemlist.append(Item(channel=item.channel, title="Trans", action="submenu", cattype="trans"))
    # itemlist.append(Item(channel=item.channel, title="Gay", action="submenu", cattype="gay"))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host, ctype="addtime", cattype=item.cattype))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host, ctype="rating_month", cattype=item.cattype))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host, ctype="comments_month", cattype=item.cattype))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host, ctype="longest", cattype=item.cattype))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories", cattype=item.cattype))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", ctype="addtime", cattype=item.cattype))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch/videos/%s/" % (host,texto)
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
    soup = create_soup(item.url).find('ul', class_='categories-list')
    matches = soup.find_all('li', class_='categories-list-item')
    # if "gay" in item.cattype:
        # matches = soup.find('div', class_='cat_box_gay').find_all('a')
    # elif "trans" in item.cattype:
        # matches = soup.find('div', class_='cat_box_trans').find_all('a')
    # else:
        # matches = soup.find('div', class_='cat_box_straight').find_all('a')
    for elem in matches:
        url = elem.a['href']
        txt = elem.find_all('span')
        title = txt[0].text.strip()
        cantidad = txt[1].text.strip()
        title = "%s %s" %(title, cantidad)
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url,url)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return itemlist


# _ga=GA1.2.1641726195.1673894730; no_popups=1; no_ads=1; traffic_type=3; no_push_notice=1; return_to=https://yeptube.com/es/; _gid=GA1.2.1402327539.1675686670; _gat=1
# _ga=GA1.2.1641726195.1673894730; no_popups=1; no_ads=1; traffic_type=3; no_push_notice=1; return_to=https://yeptube.com/es/; _gid=GA1.2.1402327539.1675686670; cattype=trans
# _ga=GA1.2.1641726195.1673894730; no_popups=1; no_ads=1; traffic_type=3; no_push_notice=1; return_to=https://yeptube.com/es/; _gid=GA1.2.1402327539.1675686670; cattype=straight
# _ga=GA1.2.1641726195.1673894730; no_popups=1; no_ads=1; traffic_type=3; no_push_notice=1; return_to=https%3A%2F%2Fyeptube.com%2Fes%2F; _gid=GA1.2.1402327539.1675686670; cattype=straight; index_filter_sort=rating_month; click_urls_1=1; video_related_with_shuffle=related; _gat=1
def create_soup(url, ctype=None, cattype=None):
    logger.info()
    accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    sec = '"document","Sec-Fetch-Dest": "document", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-User": "?1", "Pragma": "no-cache"'
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    cookie= "_ga=GA1.2.1641726195.1673894730; no_popups=1; no_ads=1; traffic_type=3; no_push_notice=1; return_to=https://yeptube.com/es/; _gid=GA1.2.916201020.1674217250; cattype=%s; index_filter_sort=%s; click_urls_1=1; video_related_with_shuffle=related; _gat=1" % (cattype, ctype)
    # sec-ch-ua-platform: "Windows"
    # "sec-ch-ua": "Not_A Brand;v=99, Google Chrome;v=109, Chromium;v=109"
    if "search" in url: 
        headers = {"Cookie": cookie, "Sec-Fetch-Dest": sec}
        data = httptools.downloadpage(url, headers=headers, canonical=canonical).data
    else:
        headers = {"Cookie": cookie ,'Referer': "%ses/" % host,'Accept': "%s" % accept, "User-Agent": UA}
        # logger.debug(headers)
        data = httptools.downloadpage(url, headers=headers, canonical=canonical).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url, item.ctype, item.cattype)
    matches = soup.find_all('div', class_='thumb-main')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        time = elem.find('span', class_='duration-badge').text.strip()
        quality = elem.find('span', class_='quality-badge')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        url = urlparse.urljoin(item.url,url)
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('span', class_='pagination-link-current')
    if next_page and next_page.parent.find_next_sibling("li"):
        next_page = next_page.parent.find_next_sibling("li").a['href']
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
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
