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
from core import jsontools as json

canonical = {
             'channel': 'pornxs', 
             'host': config.get_setting("current_host", 'pornxs', default=''), 
             'host_alt': ["https://pornxs.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

# https://pornxs.com/big-natural-tits
# https://pornxs.com/api/videos/big-natural-tits/0


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "?o=a"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ss/%s" % (host,texto)
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
    soup = get_source(item.url, soup=True)
    global pagcat
    pagcat = scrapertools.find_single_match(get_source(host), '"maxPages":(\d+)')
    matches = soup.find_all('a', class_='squares__item')
    for elem in matches:
        url = elem['href']
        title = elem.find('div', class_='squares__item_title').text.strip()
        cantidad = elem.find('span', class_='squares__item_numbers')
        if cantidad:
            title = "%s (%s)" %(title,cantidad.text.strip())
        thumbnail = elem.div['data-loader-src']
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    if "/api/" in item.url:
        current = int(scrapertools.find_single_match(item.url, '/(\d+)'))
    else:
        current = 0
    if int(current) < int(pagcat):
        page = current + 1
        next_page = "%sapi/categories/%s?o=a"  %(host,page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def get_source(url, json=False, soup=False, multipart_post=None, timeout=30, add_host=True, **opt):
    logger.info()

    opt['canonical'] = canonical
    data = httptools.downloadpage(url, soup=soup, files=multipart_post, add_host=add_host, timeout=timeout, **opt)

    # Verificamos que tenemos una sesión válida, sino, no tiene caso devolver nada
    if "Iniciar sesión" in data.data:
        # Si no tenemos sesión válida, mejor cerramos definitivamente la sesión
        global account
        if account: logout({})
        platformtools.dialog_notification("No se ha inciado sesión", "Inicia sesión en el canal {} para poder usarlo".format(__channel__))
        return None

    if json:
        data = data.json
    elif soup:
        data = data.soup
    else:
        data = data.data

    return data


def lista(item):
    logger.info()
    itemlist = []
    global name,pagcat
    if "/api/" in item.url:
        name = item.url.split("/")[5]
        name = "/%s" %name
    else:
        name = item.url
        item.url = urlparse.urljoin(host,name)
    url = urlparse.urljoin(host,name)
    pagcat = scrapertools.find_single_match(get_source(url), '"maxPages":(\d+)')
    soup = get_source(item.url, soup=True)
    matches = soup.find_all('div', class_='squares__item')
    for elem in matches:
        url = elem.a['data-embed-url']
        title = elem.a['title']
        thumbnail = elem.div['data-loader-src']
        time = elem.find('div', class_='squares__item_numbers').text.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    if "/api/" in item.url:
        current = int(scrapertools.find_single_match(item.url, '/(\d+)'))
    else:
        current = 0
    if int(current) < int(pagcat):
        page = current + 1
        next_page = "%sapi/videos%s/%s?o=a"  %(host,name,page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
