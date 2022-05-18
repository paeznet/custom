# -*- coding: utf-8 -*-
#------------------------------------------------------------

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from core import jsontools as json
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

#  https://www.fux.com  https://www.porntube.com    https://www.pornerbros.com   https://www.4tube.com  https://www.fux.com
canonical = {
             'channel': 'fux', 
             'host': config.get_setting("current_host", 'fux', default=''), 
             'host_alt': ["https://www.fux.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
url_api = "%s/api/video/list?order=%s&orientation=%s&p=1&ssr=false"


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=url_api % (host, "date", "straight")))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="lista", url=url_api %  (host, "views", "straight")))
    itemlist.append(Item(channel=item.channel, title="Mas Valorada" , action="lista", url=url_api %  (host, "rating", "straight")))
    itemlist.append(Item(channel=item.channel, title="Longitud" , action="lista", url=url_api %  (host, "duration", "straight")))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="canal", url=host + "/api/pornstar/list?order=videos&orientation=straight&p=1&ssr=false"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="canal", url=host + "/api/channel/list?order=rating&orientation=straight&p=1&ssr=false"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/api/tag/list?orientation=straight&ssr=false"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", orientation= "straight"))

    itemlist.append(Item(channel = item.channel, title = ""))
    itemlist.append(Item(channel=item.channel, title="Trans", action="submenu", orientation="shemale"))
    itemlist.append(Item(channel=item.channel, title="Gay", action="submenu", orientation="gay"))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=url_api % (host, "date", item.orientation)))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="lista", url=url_api %  (host, "views", item.orientation)))
    itemlist.append(Item(channel=item.channel, title="Mas Valorada" , action="lista", url=url_api %  (host, "rating", item.orientation)))
    itemlist.append(Item(channel=item.channel, title="Longitud" , action="lista", url=url_api %  (host, "duration", item.orientation)))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="canal", url=host + "/api/pornstar/list?order=videos&orientation=%s&p=1&ssr=false" % item.orientation))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="canal", url=host + "/api/channel/list?order=rating&orientation=%s&p=1&ssr=false" % item.orientation))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/api/tag/list?orientation=%s&ssr=false" % item.orientation))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/api/search/list?order=%s&orientation=%s&q=%s&p=1&ssr=false" % (host, "date",item.orientation, texto)
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
    if not item.orientation:
        item.orientation = "straight"
    headers = {'Referer': "%s" % host}
    data = httptools.downloadpage(item.url, headers=headers).json
    for Video in  data["tags"]["_embedded"]["items"]:
        title = Video["name"]
        thumbnail = Video["thumbDesktop"]
        dir = Video["slug"]
        url = "%s/api/tags/%s?order=%s&orientation=%s&p=1&ssr=false" %(host, dir, "date", item.orientation)
        plot = ""
        # title = "%s (%s)" % (title, vidnum)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                               thumbnail=thumbnail, plot=plot) )
    return itemlist


def canal(item):
    logger.info()
    itemlist = []
    if not item.orientation:
        item.orientation = "straight"
    headers = {'Referer': "%s" % host}
    data = httptools.downloadpage(item.url, headers=headers).json
    if "channel" in item.url:
        s= data["channels"]["_embedded"]["items"]
        page= data["channels"]["page"]
        total= data["channels"]["pages"]
        c = "channels"
    else:
        s= data["pornstars"]["_embedded"]["items"]
        page= data["pornstars"]["page"]
        total= data["pornstars"]["pages"]
        c = "pornstars"
    for Video in s:
        title = Video["name"]
        dir = Video["slug"]
        thumbnail= Video["thumbUrl"]
        vidnum = Video["videoCount"]
        url = "%s/api/%s/%s?order=date&orientation=%s&p=1&ssr=false" % (host,c,dir,item.orientation)
        plot = ""
        title = "%s (%s)" % (title, vidnum)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                               thumbnail=thumbnail, plot=plot) )
    next_page = (page+ 1)
    if next_page < total:
        next_page = re.sub(r"&p=\d+", "&p={0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="canal", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    headers = {'Referer': "%s" % host}
    data = httptools.downloadpage(item.url, headers=headers).json
    if not "/video/" in item.url and not "/search/" in item.url:
        s= data["embedded"]["videos"]["_embedded"]["items"]
        page= data["embedded"]["videos"]["page"]
        total= data["embedded"]["videos"]["pages"]
    else:
        s = data["videos"]["_embedded"]["items"]
        page= data["videos"]["page"]
        total= data["videos"]["pages"]
        
    for Video in s:
        tit = Video["title"]
        id = Video["uuid"]
        time= Video["durationInSeconds"]
        thumbnail = Video["thumbnailsList"][0]
        quality = Video["isHD"]
        url = "%s/embed/%s" % (host,id)
        time = timer(time)
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,tit)
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,tit)
        contentTitle = title
        thumbnail = thumbnail.replace("\/", "/")
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url,
                              thumbnail=thumbnail, plot=plot, contentTitle = contentTitle))
    next_page = (page+ 1)
    if next_page < total:
        next_page = re.sub(r"&p=\d+", "&p={0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def timer(segundos):
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
    return duration


def findvideos(item):
    logger.info(item)
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info(item)
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist