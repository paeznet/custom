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
from core import servertools, channeltools
from core import httptools
from bs4 import BeautifulSoup
from core.jsontools import json

canonical = {
             'channel': 'bellesa', 
             'host': config.get_setting("current_host", 'bellesa', default=''), 
             'host_alt': ["https://www.bellesa.co/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

api = "%sapi/rest/v1/videos?filter[source]=bellesa&limit=24&order[%s]=DESC&page=1"
# https://www.bellesa.co/api/rest/v1/videos?filter[source]=bellesa&limit=24&order[posted_on]=DESC&page=1

# https://www.bellesa.co/api/rest/v1/videos/filters?filter%5Bsource%5D=bellesa&limit=30


def mainlist(item):
    logger.info()
    itemlist = []
    # itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=api %(host, "posted_on") ))
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "videos?sort=recent&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "videos?sort=popular&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "videos?sort=longest&page=1"))
    itemlist.append(Item(channel=item.channel, title="Pornstar" , action="categorias", url=host + "api/rest/v1/videos/filters?filter[source]=bellesa"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "api/rest/v1/videos/filters?filter[source]=bellesa"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "api/rest/v1/videos/filters?filter[source]=bellesa"))
    # itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "videos/categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch?type=videos&sort=recent&q=%s" % (host,texto)
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
    
    data = httptools.downloadpage(item.url).json
    if "Canal" in item.title:
        data_json = data['providers']
        id = 'providers'
    elif "Categorias" in item.title:
        data_json = data['categories']
        id = 'categories'
    else:
        data_json = data['performers']
        id = 'performers'
    
    for elem in data_json:
        if elem['count'] == 0:
            continue
        name = elem['name']
        handle = elem['handle']
        count = elem['count']
        url = "%svideos?%s=%s&page=1" %(host,id,handle)
        title = "%s (%s)" %(name,count)
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


from platformcode import unify
UNIFY_PRESET = config.get_setting("preset_style", default="Inicial")
color = unify.colors_file[UNIFY_PRESET]
# color = {'movie': 'white', 'tvshow': 'salmon', 'year': 'cyan', 'rating_1': 'red', 'rating_2': 'orange',
         # 'rating_3': 'gold', 'quality': 'deepskyblue', 'cast': 'yellow', 'lat': 'limegreen', 'vose': 'firebrick',
         # 'vos': 'firebrick', 'vo': 'firebrick', 'server': 'orange', 'library': 'yellow', 'update': 'limegreen', 'no_update': 'red'}


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data_json = scrapertools.find_single_match(data, "window.__INITIAL_DATA__ = (.*?);")
    data_json = json.loads(data_json)
    for elem in data_json['videos']:  # data_json['videos']   data_json['pagination']   data_json['filters']['performers']   data_json['filters']['providers']   data_json['filters']['categories']
        id = elem['id']
        title = elem['title']
        thumbnail = elem['image']
        res = elem['resolutions']
        pornstars = elem['performers']
        canal = elem['content_provider'][0]['name']
        source = elem['source']
        segundos = elem['duration']
        
        pornstar = []
        for star in pornstars:
            pornstar.append(star['name'])
        pornstar = ' & '.join(pornstar)
        pornstar = "[COLOR %s]%s[/COLOR]" % (color.get('rating_3',''),pornstar)
        
        canal = "[COLOR %s][%s][/COLOR]" % (color.get('tvshow',''),canal)
        
        quality = res.split(',')
        quality = "[COLOR %s]%s[/COLOR]" % (color.get('quality',''),quality[-1])
        
        horas=int(segundos/3600)
        segundos-=horas*3600
        minutos=int(segundos/60)
        segundos-=minutos*60
        if segundos < 10:
            segundos = "0%s" %segundos
        if minutos < 10:
            minutos = "0%s" %minutos
        if horas == 00:
            duration = "%s:%s" % (minutos,segundos)
        else:
            duration = "%s:%s:%s" % (horas,minutos,segundos)
        time = "[COLOR %s]%s[/COLOR]" % (color.get('year',''),duration)
        
        title = "%s %s %s %s %s" %(time, quality, canal, pornstar,title)
        
        plot = pornstar
        action = "play"
        if logger.info() == False:
            action = "findvideos"        
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=source, thumbnail=thumbnail, quality=res,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    
    # next_page = scrapertools.find_single_match(data, 'title="Next page".*?href="(/videos\?page[^"]+)"')
    pages = int(scrapertools.find_single_match(data, '"pages":(\d+)'))
    page = int(scrapertools.find_single_match(data, '"page":(\d+)'))
    if page < pages:
        title="[COLOR blue]Página %s de %s[/COLOR]" %(page,pages)
        page += 1
        next_page = re.sub(r"&page=\d+", "&page={0}".format(page), item.url)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    
    resolutions = item.quality.split(",")
    for quality in resolutions:
        url = "https://s.bellesa.co/v/%s/%s.mp4" %(item.url,quality)
        itemlist.append(Item(channel=item.channel, action="play", title= quality, contentTitle = item.title, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    
    resolutions = item.quality.split(",")
    for quality in resolutions:
        url = "https://s.bellesa.co/v/%s/%s.mp4" %(item.url,quality)
        itemlist.append(['%sp' %quality, url])
    return itemlist
