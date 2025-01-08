# -*- coding: utf-8 -*-
# -*- Channel abXXX -*-
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

cnt_tot = 30

canonical = {
             'channel': 'abxxx', 
             'host': config.get_setting("current_host", 'abxxx', default=''), 
             'host_alt': ["https://abxxx.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

url_api = host + "api/json/videos2/%s/%s/%s/%s/%s.%s.1.all..%s.json"

# https://abxxx.com/api/json/videos2/3600/str/latest-updates/24/..1.all...json


def mainlist(item):
    logger.info()
    itemlist = []
    # soup = AlfaChannel.create_soup(host, alfa_s=True) #Para coger canonical
    
    itemlist.append(Item(channel=item.channel, title="Ultimas" , action="list_all", url=url_api % ("3600", "str", "latest-updates", cnt_tot, "", "", "")))
    itemlist.append(Item(channel=item.channel, title="Mejor valoradas" , action="list_all", url=url_api % ("3600", "str", "top-rated", cnt_tot, "", "", "month")))
    itemlist.append(Item(channel=item.channel, title="Mas popular" , action="list_all", url=url_api % ("3600", "str", "most-popular", cnt_tot, "", "", "month")))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="list_all",  url=url_api % ("3600", "str", "most-commented", cnt_tot, "", "", "month") ))
    itemlist.append(Item(channel=item.channel, title="Mas Largo" , action="list_all", url=url_api %  ("3600", "str", "longest", cnt_tot, "", "", "")))
    itemlist.append(Item(channel=item.channel, title="Pornstar" , action="categorias", url=host + "api/json/models/86400/%s/filt........../most-popular/%s/1.json" %("str", cnt_tot), orientation="str", domi= host, extra="models"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "api/json/channels/86400/%s/most-viewed/%s/..1.json" %("str", cnt_tot), orientation="str", domi= host, extra="channels"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "api/json/categories/14400/%s.all.en.json" %"str", orientation="str", domi= host, extra="categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar",url=host, action="search", orientation="str"))
    
    itemlist.append(Item(channel = item.channel, title = ""))
    
    itemlist.append(Item(channel=item.channel, title="Trans",url="https://abtranny.com/", action="submenu", orientation="she"))
    itemlist.append(Item(channel=item.channel, title="Gay",url="https://abgay.tube/", action="submenu", orientation="gay"))
    
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    
    url_api = item.url + "api/json/videos2/%s/%s/%s/%s/%s.%s.1.all..%s.json"
    
    itemlist.append(Item(channel=item.channel, title="Ultimas" , action="list_all", url=url_api % ("3600", item.orientation, "latest-updates", cnt_tot, "", "", ""), orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="Mejor valoradas" , action="list_all", url=url_api % ("3600", item.orientation, "top-rated", cnt_tot, "", "", "month"), orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="Mas popular" , action="list_all", url=url_api % ("3600", item.orientation, "most-popular", cnt_tot, "", "", "month"), orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="list_all",  url=url_api % ("3600", item.orientation, "most-commented", cnt_tot, "", "", "month"), orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="Mas Largo" , action="list_all", url=url_api %  ("3600", item.orientation, "longest", cnt_tot, "", "", ""), orientation=item.orientation))
    if "gay" in item.orientation:
        itemlist.append(Item(channel=item.channel, title="Pornstar" , action="categorias", url=item.url + "api/json/models/86400/%s/filt........../most-popular/%s/1.json" %("str", cnt_tot), orientation=item.orientation, domi= item.url, extra="models"))
    else:
        itemlist.append(Item(channel=item.channel, title="Pornstar" , action="categorias", url=item.url + "api/json/models/86400/%s/filt........../most-popular/%s/1.json" %(item.orientation, cnt_tot), orientation=item.orientation, domi= item.url, extra="models"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=item.url + "api/json/channels/86400/%s/most-viewed/%s/..1.json" %(item.orientation, cnt_tot), orientation=item.orientation, domi= item.url, extra="channels"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=item.url + "api/json/categories/14400/%s.all.json" %item.orientation, orientation=item.orientation,domi= item.url, extra="categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search",url = item.url, orientation=item.orientation))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%sapi/videos2.php?params=3600/%s/latest-updates/%s/search..1.all..&s=%s" % (item.url,item.orientation,cnt_tot,texto)
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
    
    data_json = httptools.downloadpage(item.url).json
    postsNumber = ""
    data = data_json['%s' %item.extra]
    for elem in data:
        cantidad = ""
        if not "categories" in item.extra:
            cantidad = elem['statistics']['videos']
        else:
            cantidad = elem['total_videos']
        title = elem['title'] 
        dir = elem['dir'] 
        thumbnail = ""
        url = "%sapi/json/videos2/3600/%s/latest-updates/%s/%s.%s.1.all...json" %(item.domi,item.orientation,cnt_tot,item.extra.replace("models", "model").replace("channels", "channel"),dir)
        if cantidad:
            title = "%s (%s)" %(title,cantidad)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="list_all", title=title, url=url,
                             thumbnail=thumbnail , plot=plot) )
                             
    if not "categories" in item.extra:
        postsNumber = data_json['total_count']
        lastpage = int(postsNumber)/cnt_tot
        if lastpage - int(lastpage) > 0:
            lastpage = int(lastpage) + 1
        page = int(scrapertools.find_single_match(item.url, '(\d+).json'))
        if page < lastpage:
            title="[COLOR blue]Página %s de %s[/COLOR]" %(page,lastpage)
            page += 1
            next_page = re.sub(r"\d+.json", "{0}.json".format(page), item.url)
            itemlist.append(Item(channel=item.channel, action="categorias", title=title, url=next_page, 
                                 domi=item.domi, orientation=item.orientation, extra=item.extra ) )
    
    return itemlist


def list_all(item):
    logger.info()
    itemlist = []
    data_json = httptools.downloadpage(item.url).json
    
    for elem in data_json['videos']:
        id = elem['video_id']
        title = elem['title']
        dir = elem['dir']
        time = elem['duration']
        thumbnail = elem['scr']
        quality = elem['file_dimensions'].split('x')[-1]
        canal = ""
        pornstar = ""
        if elem['models']:
            actors = elem['models'].split(",")
            pornstar = ' & '.join(actors)
            pornstar = "[COLOR %s] %s[/COLOR]" % (color.get('rating_3',''),pornstar)
            for elem in actors:
                title = title.replace(elem, "")
            title = title.replace(" ,,,, ", "").replace(" ,,, ", "").replace(" ,, ", "").replace(", ", "")
        
        time = "[COLOR %s] %s[/COLOR]" % (color.get('year',''),time)
        quality = "[COLOR %s] %s[/COLOR]" % (color.get('quality',''),quality)
        title = "%s %s %s %s" %(time,quality,pornstar,title)
        plot = ""
        url =  "%svideos/%s/%s/" % (host, id, dir)
        
        itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    
    postsNumber = data_json['total_count']
    lastpage = int(postsNumber)/cnt_tot
    if lastpage - int(lastpage) > 0:
        lastpage = int(lastpage) + 1
    page = int(scrapertools.find_single_match(item.url, '.(\d+).all.'))
    if page < lastpage:
        title="[COLOR blue]Página %s de %s[/COLOR]" %(page,lastpage)
        page += 1
        next_page = re.sub(r".\d+.all.", ".{0}.all.".format(page), item.url)
        itemlist.append(Item(channel=item.channel, action="list_all", title=title, url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    return itemlist

