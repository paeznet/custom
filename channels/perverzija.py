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

forced_proxy_opt = ""

canonical = {
             'channel': 'perverzija', 
             'host': config.get_setting("current_host", 'perverzija', default=''), 
             'host_alt': ["https://tube.perverzija.com/"], 
             'host_black_list': [], 
             'set_tls': None, 'set_tls_min': False, 'retries_cloudflare': 5, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'cf_assistant': False, 'CF_stat': True, 
             'CF': True, 'CF_test': False, 'alfa_s': True
             # 'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             # 'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "studio/page/1/?orderby=date"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "studio/page/1/?orderby=view"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "studio/page/1/?orderby=like"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "studio/page/1/?orderby=comment"))
    itemlist.append(Item(channel=item.channel, title="4k" , action="lista", url=host + "tag/4k-quality/page/1/?orderby=date"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="categorias", url=host + "stars/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "studios/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host+ "tags/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    itemlist.append(Item(channel=item.channel, title="-------------------"))
    itemlist.append(Item(channel=item.channel, title="Peliculas", action="movie"))

    return itemlist


def movie(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "full-movie/page/1/?orderby=date"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "full-movie/page/1/?orderby=view"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "full-movie/page/1/?orderby=like"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "full-movie/page/1/?orderby=comment"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%spage/1/?orderby=date&s=%s" % (host,texto)
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
    matches= soup.find('div', id='az-slider').find_all('li')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text.strip()
        thumbnail = ""
        plot = ""
        if "All " in title:
            action = "subcat"
        else:
            action = "lista"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    return itemlist


def subcat(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('div', id='az-slider')
    matches = soup.find_all('li')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text.strip()
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
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
    soup = create_soup(item.url).find('section', class_='video-listing')
    matches = soup.find_all('div', class_='video-item')
    for elem in matches:
        url = elem.a['href']
        if "&s=" in item.url:
            plot = elem.find('span', class_='excerpt_part').text.strip()
        else:
            plot = elem.find('div', class_='item-content').text.strip()
        title = elem.find('div', class_='item-head').a['title']
        thumbnail = elem.img['src']
        time = elem.find('span', class_='time_dur')
        if time:
            time = time.text.strip()
        else:
            time = ""
        quality = elem.find('span', class_='label hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        if "hydrax" in url:
            title = "[COLOR red]%s[/COLOR]" % title
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='nextpostslink')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.iframe['src']
    url = url.replace("index.php?", "load_m3u8_xtremestream.php?")
    data = httptools.downloadpage(url).data
    patron = r'RESOLUTION=\d+x(\d+).*?\s(http.*?&q=\d+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality, url in matches:
        itemlist.append(Item(channel=item.channel, action="play", title= quality, contentTitle = item.title, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    
    soup = create_soup(item.url)
    if soup.find('div', class_='item-tax-list'):
        pornstars = soup.find('div', class_='item-tax-list').find_all('a', href=re.compile("/stars/"))
        for x , value in enumerate(pornstars):
            pornstars[x] = value.text.strip()
        pornstar = ' & '.join(pornstars)
        pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
        lista = []
        lista.insert (0,pornstar)
        lista.insert (1,item.plot)
        item.plot = '\n'.join(lista)
    
    
    url = soup.iframe['src']
    url = url.replace("index.php?", "load_m3u8_xtremestream.php?")
    data = httptools.downloadpage(url).data
    patron = r'RESOLUTION=\d+x(\d+).*?\s(http.*?&q=\d+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality, url in matches:
        # url += '|ignore_response_code="True"'
        # url += '|Referer=%s' %url
        itemlist.append(['[perverzija] %sp' %quality, url])
    return itemlist
