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

host = 'https://xxxclub.club'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/videos?age=All&duration=All&sort=New"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/videos?age=1+month+ago&duration=All&sort=View"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/videos?age=1+month+ago&duration=All&sort=Rating"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/videos?age=All&duration=All&sort=New&search=%s" % (host,texto)
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
    matches = soup.find('div', class_='col-md-12').find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.text.strip()
        url = urlparse.urljoin(item.url,url)
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
    soup = create_soup(item.url)
    matches = soup.find_all('a', class_='linkimgholder')
    for elem in matches:
        url = elem['href']
        title = elem['title']
        thumbnail = elem.img['src']
        canal = elem.i['data-source']
        time = elem.find('span', class_='durationformat').text.strip()
        quality = elem.find('span', class_='label hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] [%s] %s" % (time,canal,title)
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('li', class_='next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    if soup.find('iframe', class_='videofw'):
        url = soup.find('iframe', class_='videofw')['src']
    else:
        url = soup.find('div', class_='col-md-8').a['href']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


# https://www.winporn.com/fr/video/1267108/spreading-amateur-ass-wide-pov       https://www.winporn.com/player_config_json/?vid=1267108&aid=0&domain_id=0&embed=0&ref=null&check_speed=0
# https://www.daftsex.com/watch/-152743714_456240532
# https://embeds.sunporno.com/embed/1559977   esta canal <video src=
# https://sexu.site/20657541   post https://sexu.site/api/video-info   videoId: 20657541
# https://desiporn.tube/video/50549/iranian-girl-big-ass-2021/    TXX
# https://www.gotporn.com/stepmom-lauren-wants-stepson-chads-creamy-load/video-16628501     source src=


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    if soup.find('iframe', class_='videofw'):
        url = soup.find('iframe', class_='videofw')['src']
    else:
        url = soup.find('div', class_='col-md-8').a['href']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
