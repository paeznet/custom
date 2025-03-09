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

forced_proxy_opt = 'ProxySSL'

# https://josporn.com/ https://www.lenporno.net/ https://en.pornohd.porn/   https://www.pornohd.sex/

canonical = {
             'channel': 'joporn', 
             'host': config.get_setting("current_host", 'joporn', default=''), 
             'host_alt': ["https://en.joporn.net"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host))
    itemlist.append(item.clone(title="Mas Popular" , action="lista", url=host + "/most-popular/"))
    itemlist.append(item.clone(title="Mejor Valorado" , action="lista", url=host + "/top-rated/"))
    itemlist.append(item.clone(title="PornStar" , action="catalogo", url=host + "/models/?sort=2"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%s/search/?text=%s" % (host,texto)
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
    soup = create_soup(item.url).find('div', class_='category')
    matches = soup.find_all('li')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text.strip()
        url = urlparse.urljoin(item.url,url)
        thumbnail = ""
        plot = ""
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='videofile')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        cantidad = elem.find('span', class_='modelsvideo')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        if cantidad.text.strip() == "0":
            title = "[COLOR red]%s[/COLOR]" % title
        url = urlparse.urljoin(item.url,url)
        plot = ""
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find(title=re.compile("Next pages"))
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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



def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='videofile')
    for elem in matches:
        if elem.find('script'):
            continue
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        time = elem.find('span', class_='duration').text.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(item.clone(action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('li', class_='active')
    if next_page and next_page.find_next_sibling("li"):
        next_page = next_page.find_next_sibling("li").a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('ul', id='downspisok').find_all('div')
    for elem in matches:
        c = elem['data-c'].split(";")
        url = "https://file%s.joporn.me/s%s/upload%s/%s/JOPORN_NET_%s_%s.mp4" %(c[2],c[2],c[3],c[0],c[0],c[1])
        quality = c[1]
        itemlist.append(item.clone(action="play", quality= quality, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    
    pornstars = soup.find_all('a', href=re.compile("/teg/"))
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    lista = item.contentTitle.split()
    lista.insert (2, pornstar)
    item.contentTitle = ' '.join(lista)
    
    
    matches = soup.find('ul', id='downspisok').find_all('div')
    for elem in matches:
        c = elem['data-c'].split(";")
        # url = "https://file%s.joporn.me/s%s/upload%s/%s/JOPORN_NET_%s_%s.mp4" %(c[2],c[2],c[3],c[0],c[0],c[1])
        url = "https://v%s.cdnde.com/x%s/upload%s/%s/JOPORN_NET_%s_%s.mp4" %(c[2],c[2],c[3],c[0],c[0],c[1])
        quality = c[1]
        itemlist.append(['.mp4 %s' %quality, url])
        # response = "480p"
        # if quality == "720p":
            # response = httptools.downloadpage(url, ignore_response_code=True).code
        # if response != 404:
            # itemlist.append(['.mp4 %s' %quality, url])
    itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return itemlist

