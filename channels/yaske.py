# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools, channeltools, tmdb
from core import httptools
# from core import jsontools as json
from lib import generictools
from modules import filtertools
from modules import autoplay


SERVER = {
          "hlswish": "streamwish", "playerwish": "streamwish", "ghbrisk": "streamwish", "iplayerhls": "streamwish",
           "listeamed": "vidguard", "1fichier":"onefichier", "luluvdo": "lulustream",
           "dhtpre": "vidhidepro", "peytonepre": "vidhidepro"
          }

IDIOMAS = {"es": "CAST", "la": "LAT", "en_ES": "VOSE", "sub-es": "VOSE"}

list_language = list(IDIOMAS.values())
list_quality = []
list_servers = list(SERVER.values())

__channel__='yaske'
__comprueba_enlaces__ = config.get_setting('comprueba_enlaces', __channel__)
__comprueba_enlaces_num__ = config.get_setting('comprueba_enlaces_num', __channel__)
try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
except:
    __modo_grafico__ = True

parameters = channeltools.get_channel_parameters(__channel__)



canonical = {
             'channel': 'yaske', 
             'host': config.get_setting("current_host", 'yaske', default=''), 
             'host_alt': ["https://yaske.ru/"], 
             'host_black_list': [], 
             'pattern': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

api = "%sapi/v1/channel/" %host

def mainlist(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Estrenos Peliculas" , action="lista", url=api + "31?returnContentOnly=true&restriction=&order=popularity:desc&perPage=50&query=&page=1"))
    itemlist.append(Item(channel=item.channel, title="Peliculas" , action="lista", url=api + "2?returnContentOnly=true&restriction=&order=popularity:desc&perPage=50&query=&page=1"))
    itemlist.append(Item(channel=item.channel, title="Estrenos Series" , action="lista", url=api + "30?0returnContentOnly=true&restriction=&order=popularity:desc&perPage=50&query=&page=1"))
    itemlist.append(Item(channel=item.channel, title="Series" , action="lista", url=api + "3?returnContentOnly=true&restriction=&order=popularity:desc&perPage=50&query=&page=1"))
    itemlist.append(Item(channel=item.channel, title="Anime" , action="lista", url=api + "117?0returnContentOnly=true&restriction=&order=popularity:desc&perPage=50&query=&page=1"))
    # itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "api/v1/value-lists/titleFilterLanguages,productionCountries,genres,titleFilterAgeRatings"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist



def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%sapi/v1/search/%s?loader=searchPage" % (host,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, referer=host, canonical=canonical).json
    if "/search/" in item.url:
        matches = data['results']
    elif data.get('pagination',''):
        matches = data['pagination']['data']
    else:
        matches = data['channel']['content']['data']
    
    for elem in matches:
        series = elem['is_series']
        title = elem['name']
        thumbnail = elem['poster']
        
        language = []
        if elem.get('availableLanguages', ''):
            idiomas = elem['availableLanguages']
            for idioma in idiomas:
                lang = idioma['language']
                language.append(IDIOMAS.get(lang, lang))

        year = '-'
        if elem.get('year', ''): year = elem['year']

        new_item = Item(channel=item.channel, title=title, thumbnail=thumbnail, 
                        language=language, infoLabels={"year": year})
        if series:
            new_item.id = elem['id']
            # new_item.id = elem['primary_video']['title_id']
            if elem.get('primary_video', ''):
                new_item.season_num = elem['primary_video']['season_num']
            new_item.url = "%sapi/v1/titles/%s/seasons/" %(host, new_item.id)
            new_item.action = "seasons"
            new_item.contentSerieName = title
        else:
            if elem.get('primary_video', ''):
                vid = elem['primary_video']['id']
                new_item.url = "%sapi/v1/watch/%s" %(host, vid)
            else:
                new_item.id = elem['id']
            new_item.action = "findvideos"
            new_item.contentTitle = title
        itemlist.append(new_item)
    
    tmdb.set_infoLabels(itemlist, True)
    
    if data.get('next_page', ''):
        next_page = data['next_page']
        if next_page:
            next_page = re.sub(r"&page=\d+", "&page={0}".format(next_page), item.url)
            itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def seasons(item):
    logger.info()
    itemlist = list()
    
    infoLabels = item.infoLabels
    
    if not item.season_num:
        url = "%sapi/v1/titles/%s?loader=titlePage" %(host, item.id)
        data = httptools.downloadpage(url, referer=host, canonical=canonical).json
        item.season_num = data['title']['primary_video']['season_num']
    
    total = int(item.season_num)
    te = 1
    while te <= total:
        season = te
        url = "%sapi/v1/titles/%s/seasons/%s?loader=seasonPage" %(host, item.id, season)
        te +=1
        if int(season) < 10:
            season = "0%s" %season
        title = "Temporada %s" % season
        infoLabels["season"] = season
        itemlist.append(Item(channel=item.channel, title=title, url=url, action="episodesxseasons",
                             infoLabels=infoLabels))
    
    tmdb.set_infoLabels_itemlist(itemlist, True)
    
    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, title="[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]", url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName))
    return itemlist


def episodesxseasons(item):
    logger.info()
    itemlist = list()
    infoLabels = item.infoLabels
    
    season = infoLabels["season"]
    
    data = httptools.downloadpage(item.url, referer=host, canonical=canonical).json
    data = data['episodes']
    for elem in data['data']:
        if elem['primary_video']:
            vid = elem['primary_video']['id']
            url = "%sapi/v1/watch/%s" %(host, vid)
            cap =  elem['primary_video']['episode_num']
            if int(cap) < 10:
                cap = "0%s" % cap
            title = "%sx%s" % (season, cap)
            infoLabels["episode"] = cap
            itemlist.append(Item(channel=item.channel, title=title, url=url, action="findvideos",
                                     infoLabels=infoLabels))
    
    tmdb.set_infoLabels_itemlist(itemlist, True)
    
    a = len(itemlist)-1
    for i in itemlist:
        if a >= 0:
            title= itemlist[a].title
            titulo = itemlist[a].infoLabels['episodio_titulo']
            title = "%s %s" %(title, titulo)
            itemlist[a].title = title
            a -= 1
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseasons(tempitem)
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    
    if not item.url:
        url = "%sapi/v1/titles/%s?loader=titlePage" %(host, item.id)
        data = httptools.downloadpage(url, referer=host, canonical=canonical).json
        vid = elem['primary_video']['id']
        item.url = "%sapi/v1/watch/%s" %(host, vid)
    data = httptools.downloadpage(item.url, referer=host, canonical=canonical).json
    series = ""
    if data['title'].get('is_series'):
        series = data['title']['is_series']
    
    videos = data['title']['videos']
    videos += data['title']['downloads']
    videos += data['alternative_videos']
    links = []
    for elem in videos:
        link = elem['src']
        hash = elem['hash']
        if hash in links:
            continue
        else: 
            links.append(hash)
        quality = elem['quality']
        lang = elem['language']
        domain = elem['domain'].split(".")[0]
        if "katfile" in domain or "nitroflare" in domain or "dailyuploads" in domain: continue
        language = IDIOMAS.get(lang, lang)
        server = SERVER.get(domain,domain)
        itemlist.append(Item(channel=item.channel, action="play", title= server, contentTitle = item.contentTitle, url=hash, language=language))
    
    # Ordenar por language
    itemlist.sort(key=lambda x: x.language)
    
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    
    
    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra !='findvideos' and not series :
        itemlist.append(Item(channel=item.channel, action="add_pelicula_to_library", 
                             title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]', url=item.url,
                             extra="findvideos", contentTitle=item.contentTitle)) 
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    
    from lib import deyaske
    url = deyaske.decrypt_link(item.url)
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
