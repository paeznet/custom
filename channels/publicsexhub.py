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
             'channel': 'publicsexhub', 
             'host': config.get_setting("current_host", 'publicsexhub', default=''), 
             'host_alt': ["https://publicsexhub.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "videos/q?orderBy=createdAt&sort=desc&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "videos/q?orderBy=views&sort=desc&page=1"))
    # itemlist.append(Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "videos/q?orderBy=duration&sort=desc&page=1"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars/q?orderBy=count&sort=desc&page=1"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%svideos/q?search=%s&orderBy=createdAt&sort=desc" % (host,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# [\"$\",\"div\",null,

# {\"className\":\"flex\",\"children\":[\"$\",\"nav\",null,{\"className\":\"flex mx-auto justify-center mt-8 text-2xl gap-1 sm:gap-2 overflow-hidden min-w-0\",\"aria-label\":\"Pagination\",\"children\":[[\"$\",\"$16\",null,{\"children\":[\"$\",\"$L1d\",null,{\"targetPage\":1,\"isDisabled\":true,\"defaultSort\":\"desc\",\"defaultOrderBy\":\"count\",\"children\":[[\"$\",\"span\",null,{\"className\":\"sr-only\",\"children\":\"Previous\"}],[\"$\",\"svg\",null,{\"xmlns\":\"http://www.w3.org/2000/svg\",\"viewBox\":\"0 0 20 20\",\"fill\":\"currentColor\",\"aria-hidden\":\"true\",\"aria-labelledby\":\"$undefined\",\"className\":\"h-8 w-24 sm:w-32\",\"children\":[null,[\"$\",\"path\",null,{\"fillRule\":\"evenodd\",\"d\":\"M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z\",\"clipRule\":\"evenodd\"}]]}]]}]}],[\"$\",\"div\",null,{\"className\":\"flex flex-shrink overflow-x-auto gap-1 sm:gap-2\",\"children\":[\"$\",\"$16\",null,

# {\"children\":[
# [\"$\",\"$L1d\",\"page-1-count-desc}\",{\"targetPage\":1,\"isActive\":true,\"defaultSort\":\"desc\",\"defaultOrderBy\":\"count\",\"children\":1}],
# [\"$\",\"$L1d\",\"page-2-count-desc}\",{\"targetPage\":2,\"isActive\":false,\"defaultSort\":\"desc\",\"defaultOrderBy\":\"count\",\"children\":2}],
# [\"$\",\"$L1d\",\"page-3-count-desc}\",{\"targetPage\":3,\"isActive\":false,\"defaultSort\":\"desc\",\"defaultOrderBy\":\"count\",\"children\":3}],
# [\"$\",\"$L1d\",\"page-4-count-desc}\",{\"targetPage\":4,\"isActive\":false,\"defaultSort\":\"desc\",\"defaultOrderBy\":\"count\",\"children\":4}],
# [\"$\",\"$L1d\",\"page-5-count-desc}\",{\"targetPage\":5,\"isActive\":false,\"defaultSort\":\"desc\",\"defaultOrderBy\":\"count\",\"children\":5}],
# [\"$\",\"$L1d\",\"page-6-count-desc}\",{\"targetPage\":6,\"isActive\":false,\"defaultSort\":\"desc\",\"defaultOrderBy\":\"count\",\"children\":6}]]}]}],
# [\"$\",\"$16\",null,{\"children\":[\"$\",\"$L1d\",null,{\"targetPage\":2,\"isDisabled\":false,\"hasMore\":true,\"defaultSort\":\"desc\",\"defaultOrderBy\":\"count\",\"children\":[[\"$\",\"span\",null,{\"className\":\"sr-only\",\"children\":\"Next\"}],


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_='grid').find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.header.text.strip()
        if elem.find('span', class_='no-thumb'):
            thumbnail = ""
        else:
            thumbnail = elem.img['src']
            thumbnail = scrapertools.find_single_match(thumbnail, '=(.*?)&')
            thumbnail = urlparse.unquote(thumbnail)
        # if "gif" in thumbnail:
            # thumbnail = elem.img['data-src']
        # if not thumbnail.startswith("https"):
            # thumbnail = "https:%s" % thumbnail
        cantidad = elem.p
        if cantidad:
            cantidad = cantidad.text.strip().replace(" videos", "")
            title = "%s (%s)" % (title,cantidad)
        url = urlparse.urljoin(item.url,url)
        if not "/actor/" in url:
            url += "?filter=latest"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find(attrs={"aria-label": "Pagination"})
    if next_page:
        next_page = next_page.find_all('a')[-1]['href']
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
    logger.debug(soup)
    matches = soup.find('div', class_='grid').find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.img['title']
        thumbnail = elem.img['src']
        thumbnail = scrapertools.find_single_match(thumbnail, '=(.*?)&')
        thumbnail = urlparse.unquote(thumbnail)
        data = elem.find_all('span', class_='p-1')
        time = data[1].text.strip()
        quality = data[0].text.strip()
        pornstars = elem.find_all('span', class_='whitespace-nowrap')
        for x , value in enumerate(pornstars):
            pornstars[x] = value.text.strip()
        if pornstars:
            pornstar = ' & '.join(pornstars)
            pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s %s" % (time,pornstar,title)
        # if quality:
            # title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        # else:
            # title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find(attrs={"aria-label": "Pagination"})
    if next_page:
        next_page = next_page.find_all('a')[-1]['href']
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
