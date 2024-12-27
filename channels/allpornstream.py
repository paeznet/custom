# -*- coding: utf-8 -*-
# -*- Channel allpornstream -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from platformcode import config, logger,unify
from core import scrapertools

from core.item import Item
from core import servertools, channeltools
from core import httptools
from bs4 import BeautifulSoup
from core.jsontools import json

UNIFY_PRESET = config.get_setting("preset_style", default="Inicial")
color = unify.colors_file[UNIFY_PRESET]

### https://allpornstream.com/   https://dayporner.com/  https://pornstellar.com/   https://sex-scenes.com/
### https://scenesxxx.com/   https://freepornfun.com/   https://redtubevids.com/  https://pornapes.com/

##############    FALTA DIVIDIR EN PAG categorias

canonical = {
             'channel': 'allpornstream', 
             'host': config.get_setting("current_host", 'allpornstream', default=''), 
             'host_alt': ["https://allpornstream.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "api/posts?page=1" ))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "api/posts?sort=views&page=1" ))
    itemlist.append(Item(channel=item.channel, title="Mejor valorados" , action="lista", url=host + "api/posts?sort=rating&page=1" ))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "api/table-list?type=producers", extra="producer" ))
    itemlist.append(Item(channel=item.channel, title="Pornstar" , action="categorias", url=host + "api/table-list?type=actors", extra="actor" ))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "api/table-list?type=categories", extra="category" ))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%sapi/posts?search=%s&page=1" % (host,texto)
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
    
    data_json = httptools.downloadpage(item.url).json
    postsNumber = ""
    
    for elem in data_json:
        cantidad = ""
        cantidad = elem['count']
        title = elem['%s' %item.extra] 
        slug = title.replace(" ", "-")
        if "producer" in item.extra:
            url = "%sapi/posts?studio=%s&page=1" %(host,slug)
        else:
            url = "%sapi/posts?%s=%s&page=1" %(host,item.extra,slug)
        if elem['thumbs_urls']:
            thumbnail = elem['thumbs_urls'][-1]['url']
        else:
            thumbnail = ""
        if cantidad:
            title = "%s (%s)" %(title,cantidad)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             thumbnail=thumbnail , plot=plot) )
                             
    # if postsNumber:
        # lastpage = postsNumber/36
        # if lastpage - int(lastpage) > 0:
            # lastpage = int(lastpage) + 1
        # page = int(scrapertools.find_single_match(item.url, 'page=(\d+)'))
        # if page < lastpage:
            # title="[COLOR blue]Página %s de %s[/COLOR]" %(page,lastpage)
            # page += 1
            # next_page = re.sub(r"&page=\d+", "&page={0}".format(page), item.url)
            # itemlist.append(Item(channel=item.channel, action="categorias", title=title, url=next_page) )
    
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data_json = httptools.downloadpage(item.url).json
    for elem in data_json['posts']:
        id = elem['_id']
        title = elem['video_title']
        slug = elem['slug']
        thumbnail = elem['image_details'][-1][-1]
        canal = ""
        if elem['producer']:
            canal = elem['producer'][0]
            if canal in title: title = title.split("]")[-1]
            canal = "[COLOR %s][%s][/COLOR]" % (color.get('tvshow',''),canal)
        if elem['actors']:
            actors = elem['actors']
            pornstar = ' & '.join(actors)
            pornstar = "[COLOR %s] %s[/COLOR]" % (color.get('rating_3',''),pornstar)
            for elem in actors:
                title = title.replace(elem, "")
            title = title.replace(" ,,,, ", "").replace(" ,,, ", "").replace(" ,, ", "").replace(", ", "")
        title = "%s %s %s" %(canal,pornstar,title)
        plot = ""
        url = "%sapi/post?id=%s" %(host, id)
        
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    
    postsNumber = data_json['count']
    lastpage = postsNumber/51
    if lastpage - int(lastpage) > 0:
        lastpage = int(lastpage) + 1
    page = int(scrapertools.find_single_match(item.url, 'page=(\d+)'))
    if page < lastpage:
        title="[COLOR blue]Página %s de %s[/COLOR]" %(page,lastpage)
        page += 1
        next_page = re.sub(r"&page=\d+", "&page={0}".format(page), item.url)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data_json = httptools.downloadpage(item.url).json
    # logger.debug(data_json['post']['video_urls']['iframe'])
    # logger.debug(data_json['post']['video_urls']['link'])
    # logger.debug(data_json['urls'])
    
    item.post = data_json['post']['video_description']
    data = data_json['urls']
    
    if isinstance(data[0], dict):
        for elem in data:
            url = elem['url']
            itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
        itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    else:
        for quality,url in data:
            itemlist.append(Item(channel=item.channel, action="play", title = quality, contentTitle = item.contentTitle, url=url))
            itemlist.reverse()
            # itemlist.append(Item(channel=item.channel, action="play",server='directo'))
            # itemlist.append(['%sp' %quality, url])
        # itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return itemlist


