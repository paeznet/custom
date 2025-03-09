# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from core import jsontools
from bs4 import BeautifulSoup

canonical = {
             'channel': 'incestflix', 
             'host': config.get_setting("current_host", 'incestflix', default=''), 
             'host_alt': ["http://www.incestflix.com/"], 
             'host_black_list': [], 
             'pattern': ["<a href='?([^'|\s*]+)['|\s*]"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
if not host.startswith("http"):
    host = "http:%s" % host


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "page/1"))
    itemlist.append(Item(channel=item.channel, title="Relation" , action="categorias", url=host + "alltags", tag="Relations</h1>(.*?)<h1>"))
    itemlist.append(Item(channel=item.channel, title="Studio" , action="categorias", url=host + "alltags", tag="Themes</h1>(.*?)<h1>"))
    itemlist.append(Item(channel=item.channel, title="Ethnicities" , action="categorias", url=host + "alltags", tag="Groups</h1>(.*?)<h1>"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "alltags", tag="Performers</h1>(.*?)</div>"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "alltags", tag="Categorized</h1>(.*?)<h1>"))
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data= scrapertools.find_single_match(data, '%s' % item.tag)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    matches = soup.find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.text
        url += "/page/1"
        thumbnail = ""
        if not url.startswith("https"):
            url = "http:%s" % url
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
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
    matches = soup.find_all('a', id="videolink")
    for elem in matches:
        url = elem['href']
        title = elem.find('div', class_='text-heading').text.strip()
        thumbnail = elem.find('div', class_='img-overflow')['style']
        thumbnail = scrapertools.find_single_match(thumbnail, 'url\(([^\)]+)')
        if thumbnail.startswith("//"):
            thumbnail = "http:%s" % thumbnail
        if not url.startswith("https"):
            url = "http:%s" % url
        plot = ""
        itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail,
                                   plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('select', id='tagpageno')
    if next_page:
        page = scrapertools.find_single_match(item.url, '(.*?)/\d+')
        next_page = next_page.find('option', selected='true')
        next_page = next_page.find_next_sibling("option")
        if next_page:
            next_page = next_page['value']
            next_page = "%s/%s" %(page, next_page)
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    else:
        next_page = soup.find('div', style=re.compile("red;")).parent
        if next_page and next_page.parent.find_next_sibling("td"):
            next_page = next_page.parent.find_next_sibling("td").a['href']
            next_page = urlparse.urljoin(item.url,next_page)
            itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s" , contentTitle=item.contentTitle, url=item.url)) 
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s" , contentTitle=item.contentTitle, url=item.url)) 
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    return itemlist
