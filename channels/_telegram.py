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
from core import filetools
from core import httptools, scrapertools, jsontools, tmdb
from core.item import Item
from core import servertools
from bs4 import BeautifulSoup

# canonical = {
             # 'channel': 'ballzdeep', 
             # 'host': config.get_setting("current_host", 'ballzdeep', default=''), 
             # 'host_alt': ["https://ballzdeep.xxx/"], 
             # 'host_black_list': [], 
             # 'pattern': ['href="?([^"|\s*]+)["|\s*]\s*rel="?stylesheet"?'], 
             # 'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             # 'CF': False, 'CF_test': False, 'alfa_s': True
            # }
# host = canonical['host'] or canonical['host_alt'][0]  https://pastebin.com/CwK5yLjx
hostb = "https://pastebin.com/raw/1V4EMK0Q"
host = "https://jqgq3705-my.sharepoint.com/:u:/g/personal/jsaezu_365civil_com/EdfU0TQ9P9pPhctIyJizZ-QB1ZPjygUF84V1L5gjCAjsUA?e=p8a8ii"
# hostb = "https://www.porntube.com/api/video/list?filter=%7B%7D&order=date&orientation=straight&ssr=false"

def mainlist(item):
    logger.info()
    itemlist = []
    # json_data = httptools.downloadpage(hostb).data
    # json_data = jsontools.load(json_data)
    path = filetools.join(config.get_data_path(), '00telegram.json')
    # logger.debug(path)
    # json = jsontools.load(filetools.read(path))
    
    json_data = filetools.read(path)
    json_data = jsontools.load(json_data)
    for elem in json_data['movies']:
        title = elem['title']
        year = elem['year']
        links = elem['links']
        thumbnail = ""
        plot = ""
        logger.debug(links)
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, contentTitle=title, links=links,
                            thumbnail=thumbnail, plot=plot, infoLabels={"year": year}))
    tmdb.set_infoLabels(itemlist, True)
    return itemlist


# def search(item, texto):
    # logger.info()
    # texto = texto.replace(" ", "-")
    # item.url = "%ssearch/%s/?sort_by=post_date&from_videos=01" % (host,texto)
    # try:
        # return lista(item)
    # except:
        # import sys
        # for line in sys.exc_info():
            # logger.error("%s" % line)
        # return []


# def categorias(item):
    # logger.info()
    # itemlist = []
    # soup = create_soup(item.url)
    # matches = soup.find_all('a', class_='item')
    # for elem in matches:
        # url = elem['href']
        # title = elem['title']
        # if elem.find('span', class_='no-thumb'):
            # thumbnail = ""
        # else:
            # thumbnail = elem.img['src']
        # if "gif" in thumbnail:
            # thumbnail = elem.img['data-src']
        # if not thumbnail.startswith("https"):
            # thumbnail = "https:%s" % thumbnail
        # cantidad = elem.find('div', class_='videos')
        # if cantidad:
            # title = "%s (%s)" % (title,cantidad.text.strip())
        # url = urlparse.urljoin(item.url,url)
        # thumbnail = urlparse.urljoin(item.url,thumbnail)
        # url += "?sort_by=post_date&from=01"
        # plot = ""
        # itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             # fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    # next_page = soup.find('li', class_='next')
    # if next_page and next_page.find('a'):
        # next_page = next_page.a['data-parameters'].split(":")[-1]
        # if "from_videos" in item.url:
            # next_page = re.sub(r"&from_videos=\d+", "&from_videos={0}".format(next_page), item.url)
        # else:
            # next_page = re.sub(r"&from=\d+", "&from={0}".format(next_page), item.url)
        # itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    # return itemlist


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


def findvideos(item):
    logger.info()
    itemlist = []
    # logger.debug(item.links)
    for elem in item.links:
        quality = scrapertools.find_single_match(str(elem), "'quality': '([^']+)'")
        url = scrapertools.find_single_match(str(elem), "'url': '([^']+)'")
        server = scrapertools.find_single_match(str(elem), "'server': '([^']+)'")
        title = "%s %sP" %(server,quality)

        itemlist.append(Item(channel=item.channel, action="play", title=title, server=server, quality=quality, contentTitle = item.contentTitle, url=url))
    return itemlist

