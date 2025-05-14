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
             'channel': 'empflix', 
             'host': config.get_setting("current_host", 'empflix', default=''), 
             'host_alt': ["https://www.empflix.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "new/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "toprated"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars?page=1"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/", extra=1))
    itemlist.append(Item(channel=item.channel, title="Buscar is out", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch?what=%s" % (host,texto)
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
    matches = soup.find_all('div', class_='mb-3')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('div', class_='thumb-title').text.strip()
        thumbnail = elem.img['src']
        cantidad = elem.span
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        if item.extra:
            url += "/new/1"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='pagination-next')
    if next_page:
        next_page = next_page.a['href']
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
    matches = soup.find_all(attrs={"data-vid": re.compile(r"^\d+")})
    for elem in matches:
        vid = elem['data-vid']
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        if "gif" in thumbnail or "placeholder.jpg" in thumbnail:
            thumbnail = elem.img['data-src']
        time = elem.find('div', class_='video-duration').text.strip()
        quality = elem.find('div', class_='max-quality')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (time,quality.text.strip(),title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, vid=vid,
                               thumbnail=thumbnail, fanart=thumbnail, contentTitle=title, plot=plot))
    next_page = soup.find('li', class_='pagination-next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    
    url = "%sajax/video-player/%s"  % (host,item.vid)
    data = httptools.downloadpage(url, canonical=canonical).json
    data = BeautifulSoup(data['html'], "html5lib", from_encoding="utf-8")
    
    matches  = data.video.find_all('source', type='video/mp4')
    for elem in matches:
        url = elem['src']
        quality = elem['size']
        itemlist.append(Item(channel=item.channel, action="play", title= "%s" %quality, contentTitle = item.contentTitle, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    
    soup = create_soup(item.url)
    if soup.find_all('a', class_="badge-kiss"):
        ### pornstars = soup.find_all('a', href=re.compile("/models/[A-z0-9-]+"))
        pornstars = soup.find_all('a', class_='badge-kiss')
        for x , value in enumerate(pornstars):
            pornstars[x] = value.text.strip()
        pornstar = ' & '.join(pornstars)
        pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
        plot = ""
        if len(pornstars) <= 3:
            lista = item.contentTitle.split('[/COLOR]')
            pornstar = pornstar.replace('[/COLOR]', '')
            pornstar = ' %s' %pornstar
            if "[COLOR red]" in item.title:
                lista.insert (2, pornstar)
            else:
                lista.insert (1, pornstar)
            item.contentTitle = '[/COLOR]'.join(lista)
        else:
            plot = pornstar
    
    url = "%sajax/video-player/%s"  % (host,item.vid)
    data = httptools.downloadpage(url, canonical=canonical).json
    data = BeautifulSoup(data['html'], "html5lib", from_encoding="utf-8")
    
    matches  = data.video.find_all('source', type='video/mp4')
    for elem in matches:
        url = elem['src']
        quality = elem['size']
        itemlist.append(["[%sp] mp4" %quality, url])
    itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return itemlist
