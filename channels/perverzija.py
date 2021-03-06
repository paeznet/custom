# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup

canonical = {
             'channel': 'perverzija', 
             'host': config.get_setting("current_host", 'perverzija', default=''), 
             'host_alt': ["https://tube.perverzija.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/studio/page/1/?orderby=date"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/studio/page/1/?orderby=view"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/studio/page/1/?orderby=like"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "/studio/page/1/?orderby=comment"))
    itemlist.append(Item(channel=item.channel, title="4k" , action="lista", url=host + "/tag/4k-quality/page/1/?orderby=date"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    itemlist.append(Item(channel=item.channel, title="Peliculas", action="movie"))

    return itemlist


def movie(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/full-movie/page/1/?orderby=date"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/full-movie/page/1/?orderby=view"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/full-movie/page/1/?orderby=like"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "/full-movie/page/1/?orderby=comment"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/page/1/?orderby=date&s=%s" % (host,texto)
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
    soup = create_soup(item.url).find('ul', class_='nav-ul-menu').find_all('ul')
    if "Canal" in item.title:
        matches = soup[1].find_all('li')
    else:
        matches = soup[3].find_all('li')
    matches.pop(0)
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
    soup = create_soup(item.url).find('section', class_='video-listing')
    matches = soup.find_all('div', class_='video-item')
    for elem in matches:
        if "&s=" in item.url:
            url = elem.a['href']
            plot = elem.find('span', class_='excerpt_part').text.strip()
        else:
            url = elem.find('div', class_='qv_tooltip')['title']
            url = scrapertools.find_single_match(url, 'src="([^"]+)"')
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
    if "index.php" in item.url:
        url = item.url.replace("index.php?", "load_m3u8_xtremestream.php?")
        logger.debug(url)
        headers = {'Referer': item.url}
        data = httptools.downloadpage(url, headers=headers).data
        # logger.debug(data)
    else:
        soup = create_soup(item.url)
        url = soup.iframe['src']
        item.url = url
        url = item.url.replace("index.php?", "load_m3u8_xtremestream.php?")
        headers = {'Referer': item.url}
        data = httptools.downloadpage(url, headers=headers).data
        # logger.debug(data)
    patron = r'#EXT-X-STREAM-INF.*?RESOLUTION=\d+x(\d+).*?\s(http.*?)\n'
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality, url in matches:
        # url += "|Referer=%s" % item.url
        itemlist.append(Item(channel=item.channel, action="play", title= quality, contentTitle = item.title, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    if "index.php" in item.url:
        url = item.url.replace("index.php?", "load_m3u8_xtremestream.php?")
    else:
        soup = create_soup(item.url)
        url = soup.iframe['src']
        item.url = url
        url = item.url.replace("index.php?", "load_m3u8_xtremestream.php?")
    url += "|Referer=%s" % item.url
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
