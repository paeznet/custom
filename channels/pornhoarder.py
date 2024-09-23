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
from modules import autoplay


list_quality = ['default']
list_servers = []


canonical = {
             'channel': 'pornhoarder', 
             'host': config.get_setting("current_host", 'pornhoarder', default=''), 
             'host_alt': ["https://ww9.pornhoarder.tv/"], 
             'host_black_list': ["https://ww8.pornhoarder.tv/", "https://ww1.pornhoarder.tv/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
url_api = host + "ajax_search.php"

netu= "servers%5B%5D=21&servers%5B%5D=40&servers%5B%5D=12&servers%5B%5D=35&servers%5B%5D=39&servers%5B%5D=26&servers%5B%5D=25&servers%5B%5D=41&servers%5B%5D=17"

def mainlist(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url="search=&sort=0&date=0&%s&author=0&page=1" %netu))
    itemlist.append(Item(channel=item.channel, title="Mas vistas" , action="list_all", url="search=&sort=1&date=3&%s&author=0&page=1" %netu))
    itemlist.append(Item(channel=item.channel, title="Mas populares" , action="list_all", url="search=&sort=2&date=3&%s&author=0&page=1" %netu))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars/?page=1"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "studios/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "search=%s&sort=0&date=0&%s&author=0&page=1" % (texto,netu)
    try:
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('article')
    for elem in matches:
        if "categories" in item.url:
            texto = elem.a['href'].replace("/search/?search=", "")
            url = "search=%s&sort=0&date=0&%s&author=0&page=1" % (texto,netu)
        else:
            url = elem.a['href']
            url = urlparse.urljoin(item.url,url)
        title = elem.h2.text#elem.a['title']
        if elem.find('div', class_='video-image'):
            thumbnail = elem.find('div', class_='video-image')['data-src']
        else:
            thumbnail = ""
        if "gif" in thumbnail:
            thumbnail = elem.img['data-src']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        cantidad = elem.find('div', class_='video-conunt')
        if elem.find('div', class_='video-content-meta'):
            cantidad = elem.find('div', class_='video-content-meta')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        if not "categories" in item.url:
            url += "videos/"
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="list_all", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        post = referer
        referer = "%ssearch/?%s" %(host,referer.replace("+", "%20"))
        ct = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers={'Content-Type': ct, 'Referer': referer}
        data = httptools.downloadpage(url, headers=headers, post=post, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def list_all(item):
    logger.info()
    itemlist = []
    if "search=" in item.url:
        soup = create_soup(url_api, referer=item.url)
    else:
        soup = create_soup(item.url)
    matches = soup.find_all('article')#('div', class_=re.compile(r"^item-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.h1.text
        thumbnail = elem.find('div', class_='video-image')['data-src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-original']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        if elem.find('img'):
           canal = elem.find('div', class_='item').get_text(strip=True)
           server = scrapertools.find_single_match(canal, '(\w+)')
           title = "%s [COLOR orange]%s[/COLOR] " % (title,canal)
        time = elem.find('div', class_='video-length').get_text(strip=True) if elem.find('div', class_='video-length') else ''
        if time:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(host,url)
        plot = ""
        # action = "play"
        # if logger.info() == False:
            # action = "findvideos"
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, contentTitle=title, url=url, server=server,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='next')
    if "search=" in item.url and next_page and next_page.find('span'):
        next_page = next_page.span['data-page']
        next_page = re.sub(r"&page=\d+", "&page={0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="list_all", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    elif  next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="list_all", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    
    soup = create_soup(item.url)
    plot = ""
    if soup.find_all('a', href=re.compile(r"/pornstar/[A-z0-9-]+/")):
        pornstars = soup.find_all('a', href=re.compile(r"/pornstar/[A-z0-9-]+/"))
        for x, value in enumerate(pornstars):
            pornstars[x] = value.h4.get_text(strip=True)
        pornstar = ' & '.join(pornstars)
        pornstar = "[COLOR cyan]%s" % pornstar
        lista = item.contentTitle.split("[/COLOR]")
        if "[COLOR yellow]" in lista[0]:
            lista.insert (1, pornstar)
        else:
            lista.insert (0, pornstar)
        item.contentTitle = '[/COLOR] '.join(lista)
        plot = '%s[/COLOR]' %pornstar
    
    
    itemlist.append(Item(channel=item.channel, action="play", title=item.server.capitalize(), server=item.server.capitalize(), url=item.url, contentTitle = item.contentTitle, plot=plot))
    
    if soup.find('ul', class_='server-list'):
        matches = soup.find('ul', class_='server-list').find_all("a")
        for elem in matches:
            url = elem['href']
            url = urlparse.urljoin(host,url)
            server = elem.text.strip().capitalize()
            itemlist.append(Item(channel=item.channel, action="play", title=server, contentTitle = item.contentTitle, server=server, url=url))
    
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    
    return itemlist



def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.iframe['src']
    
    id = scrapertools.find_single_match(url, "video=(.*?)")
    post = {'video': id, 'play':''}
    
    data = httptools.downloadpage(url, post=post, canonical=canonical).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    url = soup.iframe['src']
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

