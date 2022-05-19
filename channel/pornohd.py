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

# https://en.pornohd.porn  https://en.joporn.net   https://josporn.com/ https://www.lenporno.net/  https://www.pornohd.sex/
canonical = {
             'channel': 'pornohd', 
             'host': config.get_setting("current_host", 'pornohd', default=''), 
             'host_alt': ["https://en.pornohd.porn"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/new-update/page-1/"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/most-popular/page-1/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/the-best/page-1/"))
    # itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "/most-commented/1/?sort_by=most_commented_month&from=01"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="catalogo", url=host + "/best-models/"))
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/sites/?sort_by=avg_videos_popularity&from=01"))

    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
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
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='category_tegs')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('div', class_='category_name').text.strip()
        thumbnail = elem.img['src']
        cantidad = elem.find('span', class_='video')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        if cantidad.text.strip() == "0":
            title = "[COLOR red]%s[/COLOR]" % title
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='preview_screen')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        cantidad = elem.find('div', class_='video')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        if cantidad.text.strip() == "0":
            title = "[COLOR red]%s[/COLOR]" % title
        url = urlparse.urljoin(item.url,url)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('div', class_='mobnavigation')
    if next_page:
        next_page = next_page.find_all('a')[-1]['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    matches = soup.find_all('div', class_='preview_screen')
    for elem in matches:
        if "Advertisement" in elem.text:
            continue
        else:
            url = elem.a['href']
            title = elem.img['alt']
            thumbnail = elem.img['src']
            time = elem.find('div', class_='duration').text.strip()
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('div', class_='mobnavigation')
    if next_page:
        next_page = next_page.find_all('a')[-1]['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('ul', id='downspisok').find_all('div')
    for elem in matches:
        c = elem['data-c'].split(";")
        url = "https://v%s.cdnde.com/x%s/upload%s/%s/JOPORN_NET_%s_%s.mp4" %(c[2],c[2],c[3],c[0],c[0],c[1])
        quality = c[1]
        itemlist.append(Item(channel=item.channel, action="play", quality= quality, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    pornstars = soup.find_all('a', href=re.compile("/model/"))
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    if pornstars:
        pornstar = ' & '.join(pornstars)
        pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
        lista = item.contentTitle.split()
        lista.insert (2, pornstar)
        item.contentTitle = ' '.join(lista)
    matches = soup.find('ul', id='down_spisok').find_all('div')
    for elem in matches:
        c = elem['data-c'].split(";")
        url = "https://v%s.cdnde.com/x%s/upload%s/%s/JOPORN_NET_%s_%s.mp4" %(c[2],c[2],c[3],c[0],c[0],c[1])
        quality = c[1]
        # response = "480p"
        # if quality == "720p":
            # response = httptools.downloadpage(url, ignore_response_code=True).code
        # if response != 404:
        itemlist.append(['.mp4 %s' %quality, url])
        itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return itemlist
