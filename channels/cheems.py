# -*- coding: utf-8 -*-
# -*- Channel Cheems -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger,unify
from core import scrapertools

from core.item import Item
from core import servertools, channeltools
from core import httptools
from bs4 import BeautifulSoup
from core.jsontools import json
from modules import autoplay

UNIFY_PRESET = config.get_setting("preset_style", default="Inicial")
color = unify.colors_file[UNIFY_PRESET]


list_quality = []
list_servers = []

#########           Falla visualizacion de thumbnails

canonical = {
             'channel': 'cheems', 
             'host': config.get_setting("current_host", 'cheems', default=''), 
             'host_alt': ["https://cheemsporno.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

api = "%sapi/%s?perPage=36&orderBy=%s&order=desc&page=1"

def mainlist(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=api %(host, "posts", "date") ))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=api %(host, "posts", "views") ))
    itemlist.append(Item(channel=item.channel, title="Pornstar" , action="categorias", url=api %(host, "actors", "views") ))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=api %(host, "producers", "views") ))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "_next/data/IPiH7-r6cZNpzsbHsG-3c/es/tags.json", extra="Categorias" ))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%sapi/posts?perPage=36&orderBy=date&order=desc&postTitle=%s&page=1" % (host,texto)
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
    
    postsNumber = ""
    if "producers" in item.url:
        data_json = data['producers']
        postsNumber = data['producersNumber']
        extra = 'producer'
    elif "actors" in item.url:
        data_json = data['actors']
        postsNumber = data['actorsNumber']
        extra = 'actor'
    else:
        data_json = data['pageProps']['tagCards']
        extra = 'tag'
    
    for elem in data_json:
        cantidad = ""
        if not "tag" in item.url:
            cantidad = elem['postsNumber']
            elem = elem['%s' % extra]
        name = elem['name']
        slug = elem['slug']
        thumbnail = elem['imageUrl']
        
        url = "%sapi/posts?perPage=36&orderBy=date&order=desc&%sSlug=%s&page=1" %(host,extra,slug)
        title = name
        if cantidad:
            title = "%s (%s)" %(title,cantidad)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             thumbnail=thumbnail , plot=plot) )
    if item.extra:
        itemlist.sort(key=lambda x: x.title)
    if postsNumber:
        lastpage = postsNumber/36
        if lastpage - int(lastpage) > 0:
            lastpage = int(lastpage) + 1
        page = int(scrapertools.find_single_match(item.url, 'page=(\d+)'))
        if page < lastpage:
            title="[COLOR blue]Página %s de %s[/COLOR]" %(page,lastpage)
            page += 1
            next_page = re.sub(r"&page=\d+", "&page={0}".format(page), item.url)
            itemlist.append(Item(channel=item.channel, action="categorias", title=title, url=next_page) )
    
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
    data_json = httptools.downloadpage(item.url).json
    for elem in data_json['posts']:
        canal = ""
        id = elem['post']['id']
        title = elem['post']['title']
        slug = elem['post']['slug']
        for v in elem['post']['meta']:
            if "duration" in v['type']: segundos = v['value'].split(".")[0]
            if "resolution" in v['type']: quality = v['value']
            if "thumb" in v['type']: thumbnail = v['value']
        if elem['post']['producer']:
            canal = elem['post']['producer']['name']
            canal = "[COLOR %s][%s][/COLOR]" % (color.get('tvshow',''),canal)
        quality = "[COLOR %s][%s][/COLOR]" % (color.get('quality',''),quality)
        plot = elem['post']['description']
        
        segundos = int(segundos)
        horas=int(segundos/3600)
        segundos -=horas*3600
        minutos =int(segundos/60)
        segundos-=minutos*60
        if segundos < 10:
            segundos = "0%s" %segundos
        if minutos < 10:
            minutos = "0%s" %minutos
        if horas == 00:
            duration = "%s:%s" % (minutos,segundos)
        else:
            duration = "%s:%s:%s" % (horas,minutos,segundos)
        time = "[COLOR %s]%s[/COLOR]" %(color.get('year',''),duration)
        
        if canal:
            title = "%s %s %s %s" %(time, quality, canal, title)
        else:
            title = "%s %s %s" %(time, quality, title)
        
        url = "%sposts/videos/%s" %(host, slug)
        
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    
    postsNumber = data_json['postsNumber']
    lastpage = postsNumber/36
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
    data = httptools.downloadpage(item.url).data
    # soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    # pornstars = soup.find_all('a', href=re.compile("/actors/[A-z0-9-]+"))
    # for x , value in enumerate(pornstars):
        # pornstars[x] = value.text.strip()
    # pornstar = ' & '.join(pornstars)
    # pornstar = "[COLOR %s]%s[/COLOR]" % (color.get('rating_3',''),pornstar)
    # lista = item.contentTitle.split('[/COLOR]')
    # pornstar = pornstar.replace('[/COLOR]', '')
    # if color.get('tvshow','') in item.title:
        # lista.insert (2, pornstar)
    # else:
        # lista.insert (1, pornstar)
    # item.contentTitle = '[/COLOR]'.join(lista)
    
    patron = '\{"title":"([^"]+)"."url":"([^"]+)","type":'
    matches = scrapertools.find_multiple_matches(data, patron)
    copias=[]
    for serv, url in matches:
        if "cheems" in url: continue
        marca = url.split("/")[-1].replace("embed-", "")
        if not marca in copias: 
            copias.append(marca)
            itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    
    return itemlist


