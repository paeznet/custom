# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse
import re

from platformcode import config, logger
from core import scrapertools
from core import servertools
from core.item import Item
from core import httptools
from channels import filtertools
from bs4 import BeautifulSoup
from channels import autoplay

IDIOMAS = {'vo': 'VO'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = ['verystream']

canonical = {
             'channel': 'pornhive', 
             'host': config.get_setting("current_host", 'pornhive', default=''), 
             'host_alt': ["https://pornhive.tv"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

# link caidos

def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append( Item(channel=item.channel, title="Peliculas" , action="lista", url=host + "/movie/"))
    itemlist.append( Item(channel=item.channel, title="Canal" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/search?keyword=%s" % texto
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
    data = httptools.downloadpage(item.url).data
    if item.title == "Categorias" :
        data = scrapertools.find_single_match(data,'Categories(.*?)Channels')
    else:
        data = scrapertools.find_single_match(data,'Channels(.*?)</ul>')
    patron  = '<li><a href="([^"]+)" title="[^"]+">(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail, plot=scrapedplot) )
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
    matches = soup.find_all('div', class_='card-movie-poster')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('meta', itemprop='name')['content']
        thumbnail = elem.img['src']
        time = elem.find('div', class_='card-movie-duration')
        if time:
            time = time.text.strip()
            title = "[COLOR yellow]%s[/COLOR] %s" % (time, title)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, contentTitle = title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot))
    next_page = soup.find(attrs={"aria-label": "Next"})
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist

# https://pornhive.tv/movie/ripe-9/

# <div id="watch-sources">
          # <div class="bg-dark border p-3 d-flex flex-wrap align-items-center pb-0">
            # <span class="me-3">Stream</span>
              # <button type="button" id="embed_1" data-id="2622" data-method="view" class="btn btn-primary me-2 mb-3 btn-sm btn-click btn-play-server"><i class="bi bi-play-fill"></i> dood.to</button>
              # <button type="button" id="embed_2" data-id="2622" data-method="view" class="btn btn-primary me-2 mb-3 btn-sm btn-click btn-play-server"><i class="bi bi-play-fill"></i> highstream.tv</button>
              # <button type="button" id="embed_3" data-id="2622" data-method="view" class="btn btn-primary me-2 mb-3 btn-sm btn-click btn-play-server"><i class="bi bi-play-fill"></i> mangovideo.club</button>
              # <button type="button" id="embed_4" data-id="2622" data-method="view" class="btn btn-primary me-2 mb-3 btn-sm btn-click btn-play-server"><i class="bi bi-play-fill"></i> netu.wiztube.xyz</button>
              # <button type="button" id="embed_5" data-id="2622" data-method="view" class="btn btn-primary me-2 mb-3 btn-sm btn-click btn-play-server"><i class="bi bi-play-fill"></i> streamzz.to</button>
              # <button type="button" id="embed_6" data-id="2622" data-method="view" class="btn btn-primary me-2 mb-3 btn-sm btn-click btn-play-server"><i class="bi bi-play-fill"></i> videobin.co</button>
              # <button type="button" id="embed_7" data-id="2622" data-method="view" class="btn btn-primary me-2 mb-3 btn-sm btn-click btn-play-server"><i class="bi bi-play-fill"></i> youdbox.com</button>
          # </div>
  # </div>
# var ajax_object = {"ajaxurl":"https:\/\/pornhive.tv\/wp-admin\/admin-ajax.php","ajax_nonce":"2cd0718245"}; 


 
# POST  https://pornhive.tv/wp-admin/admin-ajax.php
# action=av_tube_movie_vote&id=2622&method=view&key=2cd0718245

def findvideos(item):
    import base64
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = ';extra_urls\[\d+\]=\'([^\']+)\''
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl in matches:
        url = base64.b64decode(scrapedurl).decode('utf-8')
        if "strdef" in url: 
            url = decode_url(url)
            if "strdef" in url:
                url = httptools.downloadpage(url).url
        elif "vcdn." in url:
            server = "fembed"

###################################### ES FEMBED

        # elif "vcdn" in url:
            # url = url.replace("https://vcdn.pw/v/", "https://vcdn.pw/api/source/")
            # post = "r=&d=vcdn.pw"
            # data1 = httptools.downloadpage(url, post=post).data
            # scrapedurl = scrapertools.find_single_match(data1,'"file":"([^"]+)"')
            # url = scrapedurl.replace("\/", "/")
            # url = httptools.downloadpage(url).url
##########################################
            itemlist.append(Item(channel=item.channel, action="play", server= server, url=url))
        # itemlist.append(Item(channel=item.channel, action="play", title="%s", url=url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 


    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist


def decode_url(txt):
    import base64
    logger.info()
    itemlist = []
    data = httptools.downloadpage(txt).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    rep = True
    while rep == True:
        b64_data = scrapertools.find_single_match(data, '\(dhYas638H\("([^"]+)"\)')
        if b64_data:
            b64_url = base64.b64decode(b64_data + "=").decode("utf8")
            b64_url = base64.b64decode(b64_url + "==").decode("utf8")
            data = b64_url
        else:
            rep = False
    url = scrapertools.find_single_match(b64_url, '<iframe src="([^"]+)"')
    return url
