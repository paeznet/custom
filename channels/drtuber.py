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
             'channel': 'drtuber', 
             'host': config.get_setting("current_host", 'drtuber', default=''), 
             'host_alt': ["https://www.drtuber.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel = item.channel, title="Nuevos" , action="lista", url=host, ctype="addtime"))
    itemlist.append(Item(channel = item.channel, title="Mejor valorado" , action="lista", url=host, ctype="rating_month"))
    itemlist.append(Item(channel = item.channel, title="Mas largo" , action="lista", url=host, ctype="longest"))
    itemlist.append(Item(channel = item.channel, title="PornStar" , action="catalogo", url=host + "/pornstars"))
    itemlist.append(Item(channel = item.channel, title="Canal" , action="catalogo", url=host + "/channels", cattype="straight"))
    itemlist.append(Item(channel = item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append(Item(channel = item.channel, title="Buscar", action="search", ctype="addtime"))

    itemlist.append(Item(channel = item.channel, title = ""))
    itemlist.append(Item(channel = item.channel, title="Gay", action="submenu", cattype="gay"))
    itemlist.append(Item(channel = item.channel, title="Trans", action="submenu", cattype="shemale"))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    url = "%s%s" %(host,item.cattype)
    if "shemale" in item.cattype:
        item.cattype = "trans"

    itemlist.append(Item(channel = item.channel, title="Nuevos" , action="lista", url=url, ctype=""))
    itemlist.append(Item(channel = item.channel, title="Mejor valorado" , action="lista", url=url, ctype="rating_month"))
    itemlist.append(Item(channel = item.channel, title="Mas largo" , action="lista", url=url, ctype="longest"))
    itemlist.append(Item(channel = item.channel, title="Canal" , action="catalogo", url=host + "channels"))
    itemlist.append(Item(channel = item.channel, title="Categorias" , action="categorias", url=url))
    # itemlist.append(Item(channel = item.channel, title="Buscar", action="search"))
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
    soup = create_soup(item.url)
    if "gay" in item.url:
        matches = soup.find_all('a', href=re.compile(r"^/gay/categories/"))
    elif "shemale" in item.url:
        matches = soup.find_all('a', href=re.compile(r"^/shemale/categories/"))
    else:
        matches = soup.find('div', class_='drop_inner').find_all('a', href=re.compile(r"^/categories/"))
    for elem in matches:
        url = elem['href']
        title = elem.text
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url,url)
        itemlist.append(Item(channel = item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url, "", item.cattype)
    matches = soup.find_all('a', class_='thumb')
    for elem in matches:
        url = elem['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        cantidad = elem.find('em', title='video')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel = item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel = item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def create_soup(url, ctype=None, cattype=None):
    logger.info()
    if ctype:
        headers = {"Cookie": "index_filter_sort=%s" % ctype}
        data = httptools.downloadpage(url, headers=headers, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if cattype:
        headers = {"Cookie": "cattype=%s" % cattype}
        data = httptools.downloadpage(url, headers=headers, canonical=canonical).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    if "search" in item.url:
      soup = create_soup(item.url, "", item.cattype)
    else:
        soup = create_soup(item.url, item.ctype)
    matches = soup.find_all('a', class_='ch-video')
    for elem in matches:
        url = elem['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        time = elem.find('em', class_='time_thumb').text.strip()
        quality = elem.find('i', class_='ico_hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        url = urlparse.urljoin(item.url,url)
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel = item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('li', class_='next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel = item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel = item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

def play(item):
    logger.info()
    itemlist = []
    
    soup = create_soup(item.url)
    class_='categories_list'
    if soup.find('div', class_='categories_list').find_all('a', href=re.compile("/pornstar/[A-z0-9-]+")):
        pornstars = soup.find('div', class_='categories_list').find_all('a', href=re.compile("/pornstar/[A-z0-9-]+"))
        for x , value in enumerate(pornstars):
            pornstars[x] = value.text.strip()
        pornstar = ' & '.join(pornstars)
        pornstar = "[COLOR cyan]%s" % pornstar
        lista = item.contentTitle.split("[/COLOR]")
        if "HD" in item.title:
            lista.insert (2, pornstar)
        else:
            lista.insert (1, pornstar)
        item.contentTitle = ' [/COLOR]'.join(lista)    
    itemlist.append(Item(channel = item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
