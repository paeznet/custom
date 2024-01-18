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
             'channel': 'orgasmatrix', 
             'host': config.get_setting("current_host", 'orgasmatrix', default=''), 
             'host_alt': ["https://www.orgasmatrix.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Noticias" , action="lista", url=host))
    itemlist.append(Item(channel=item.channel, title=">>>>> Buscar Noticias", action="search", type="noticias"))
    itemlist.append(Item(channel=item.channel, title="Tube" , action="lista", url=host + "pornotube/"))
    itemlist.append(Item(channel=item.channel, title=">>>>> Buscar Videos", action="search", type="videos"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "actrices-porno/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "productoras/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="catalogo", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist

# ?filter=videos  productoras noticias
def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch/%s/?filter=videos" % (host,texto)
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
    matches = soup.find_all('article', id=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        if elem.find('span', class_='no-thumb'):
            thumbnail = ""
        else:
            thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-src']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        cantidad = elem.find('span', class_='text')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        # url = urlparse.urljoin(item.url,url)
        # thumbnail = urlparse.urljoin(item.url,thumbnail)
        url += "?sort_by=post_date&from=01"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='next')
    if next_page and next_page.find('a'):
        next_page = next_page.a['data-parameters'].split(":")[-1]
        if "from_videos" in item.url:
            next_page = re.sub(r"&from_videos=\d+", "&from_videos={0}".format(next_page), item.url)
        else:
            next_page = re.sub(r"&from=\d+", "&from={0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('ul', class_='header-cats')
    matches = soup.find_all('li')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text.strip()
        thumbnail = ""
        url = urlparse.urljoin(item.url,url)
        # thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
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
    matches = soup.find_all('article', id=re.compile(r"^post-\d+"))
    # matches = soup.find_all('article', class_='post')
    for elem in matches:
        time = ""
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-src']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        time = elem.find('span', string=re.compile(r"^\d+:\d+"))
        if time:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time.text.strip(),title)
        plot = ""
        if not "/video/" in url:
            action = "lista2"
        else:
            action="play"
        if not "site" in elem['class']:
            itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                                 fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista2(item):
    logger.info()
    itemlist = []
    titles = ""
    soup = create_soup(item.url).find('div', class_='article-content')
    plot = soup.find_all('p')
    for x , value in enumerate(plot):
        plot[x] = value.text.strip()
    plot = '\n\n'.join(plot)
    if soup.find('h3'):
        titles = soup.find_all('h3')
    matches = soup.find_all('iframe')
    for elem in matches:
        url = elem['data-src']
        title = item.contentTitle
    # if titles:
        # for elem, elem2 in zip(matches, titles):
            # url = elem['data-src']
            # title = elem2.text.strip()
        # itemlist.append(Item(channel=item.channel, action="play", title= title, contentTitle = item.contentTitle, url=url, plot = plot))
    # else:
        # for elem in matches:
            # url = elem['data-src']
            # title = item.contentTitle
        itemlist.append(Item(channel=item.channel, action="play", title= title, contentTitle = item.contentTitle, url=url, plot = plot))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    if "/video/" in item.url:
        soup = create_soup(item.url, referer=host).find('div', class_='article-content')
        elem = soup.find('iframe')
        if elem.get("data-src", ""):
            url = elem['data-src']
        else:
            url = elem['src']
        if "xh" in url:
            url = "https:%s" %url
            url = httptools.downloadpage(url).url
        if "player.php" in url:
            url = url.replace("player.php", "getVideo.php")
            data = httptools.downloadpage(url, timeout= 20, referer=item.url).json
            # logger.debug(data)
            url = data['videoUrl']
            ext= url[-4:]
            # url += "|ignore_response_code=True"
            # url += "|Referer=%s" % host
            itemlist.append(item.clone(action="play", contentTitle = item.contentTitle, url=url, server='directo'))
            # itemlist.append(["[orgasmatrix] %s" %ext, url])
        else:
            itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.contentTitle, url=url))
            itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    else:
        if "player.php" in item.url:
            url = item.url.replace("player.php", "getVideo.php")
            data = httptools.downloadpage(url, timeout= 20, referer=item.url).json
            url = data['videoUrl']
            if url:
                ext= url[-4:]
                # url += "|ignore_response_code=True"
                # url += "|Referer=%s" % host
                itemlist.append(item.clone(action="play", contentTitle = item.contentTitle, url=url, server='directo'))
                # itemlist.append(["[orgasmatrix] %s" %ext, url])
            else:
                return
        else:
            itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
            itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

