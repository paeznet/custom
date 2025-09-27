# -*- coding: utf-8 -*-
# -*- Channel Cuevana2español -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

from channelselector import get_thumb
from modules import autoplay
from modules import filtertools
from core import httptools
from core import jsontools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger

list_quality = []
list_servers_black = {"netu"}
list_serversx = {'filemoon' : 'tiwikiwi', 'vidhide' : 'vidhidepro'}
list_servers = ['streamwish', 'tiwikiwi', 'voes', 'doodstream', 'streamtape', 'plushstream', 'vidhide']
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'cuevana2espanol', 
             'host': config.get_setting("current_host", 'cuevana2espanol', default=''), 
             'host_alt': ["https://www.cuevana2espanol.net/"], 
             'host_black_list': ["https://www.cuevana2espanol.icu/", "https://cuevana2espanol.com/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt,  
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

encoding = "utf-8"

try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
except:
    __modo_grafico__ = True


timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/pelicula"
tv_path = '/serie'
language = []
url_replace = []

def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Peliculas', action='sub_menu', url=host+'archives/movies/', 
                         thumbnail=get_thumb('movies', auto=True), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title='Series',  action='sub_menu', url=host+'archives/series/', 
                         thumbnail=get_thumb('tvshows', auto=True), c_type='series'))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host,
                         thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Últimas', url=item.url + "page/", action='list_all', pagina=1,
                         thumbnail=get_thumb('all', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, title='Estrenos', url=item.url+'releases/page/', action='list_all', pagina=1, 
                         thumbnail=get_thumb('all', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, title='Top Semana', url=item.url+'top/week/page/', action='list_all', pagina=1, 
                         thumbnail=get_thumb('all', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, title='Top Día', url=item.url+'top/day/page/', action='list_all', pagina=1,
                         thumbnail=get_thumb('all', auto=True), c_type=item.c_type))
    
    if item.c_type == 'peliculas':
        itemlist.append(Item(channel=item.channel, title='Generos', action='section', url=host,
                             thumbnail=get_thumb('genres', auto=True), c_type=item.c_type))
    else:
        itemlist.append(Item(channel=item.channel, title='Episodios', action='list_all', url=host+'archives/episodes',
                             thumbnail=get_thumb('episodes', auto=True), c_type='episodios'))

    return itemlist


def section(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(host + "_next/static/chunks/170-ffbd7aad7b82d5af.js", encoding="unicode_escape").data
    data = data.decode('unicode_escape')
    patron = 'href:"(/genres/.+?)".+?children:"(.+?)"'
    logger.info("patron: %s" %(type(patron)))
    logger.info("data: %s" %type(data))
    matches = scrapertools.find_multiple_matches(data, patron)
    
    for url, title in matches:
        itemlist.append(Item(channel=item.channel, title=title, action='list_all', url=host+url+"/page/", pagina=1,
                             thumbnail=get_thumb('episodes', auto=True) ))

    genres = {'Acción': 'genres/accion/', 
              'Animación': 'genres/animacion/', 
              'Crimen': 'genres/crimen/', 
              'Familia': 'genres/familia/', 
              'Misterio': 'genres/misterio/', 
              'Suspense': 'genres/suspenso/', 
              'Aventura': 'genres/aventura/', 
              'Ciencia Ficción': 'genres/ciencia-ficcion/', 
              'Drama': 'genres/drama/', 
              'Fantasía': 'genres/fantasia/', 
              'Romance': 'genres/romance/', 
              'Terror': 'genres/terror/'
              }

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url + "%s" %item.pagina, canonical=canonical).data
    patron  = '(?ims)(?:bdOz3|_LFJR).*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<h3>([^<]+).*?'
    patron += '<span>([^<]+).*?'
    matches = scrapertools.find_multiple_matches(data, patron)
    
    for url, title, annio in matches:
        idioma = "Latino"
        item.infoLabels['year'] = annio
        #para los titulos que vienen como este: The killer&#x27;s game   | moll&#x27;s game
        title = scrapertools.unescape(title)
        # itemlist.append(item.clone(channel = item.channel,
                                   # action = "findvideos",
                                   # title = title,
                                   # contentTitle = title,
                                   # thumbnail = "",
                                   # url = url,
                                   # contentType="movie",
                                   # language = idioma
                                   # ))
        new_item = Item(channel=item.channel, url=url, title=title, thumbnail="", c_type =item.c_type,
                        language=idioma, infoLabels={"year": annio})
        if "series" in item.ctype:
            new_item.action = "seasons"
            new_item.contentSerieName = title
        else:
            new_item.action = "findvideos"
            new_item.contentTitle = title
        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    url_pagina = scrapertools.find_single_match(data, 'class="page-link" href="([^"]+)')
    if url_pagina != "":
        paginax = "Pagina: %s" %(item.pagina + 1)
        itemlist.append(Item(channel = item.channel, action = "list_all", title = paginax, url = item.url, pagina = item.pagina + 1))
    return itemlist


def seasons(item):
    logger.info()

    return AlfaChannel.seasons(item, **kwargs)


def episodios(item):
    logger.info()
    
    itemlist = []
    
    templist = seasons(item)
    
    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()

    kwargs['matches_post_get_video_options'] = findvideos_matches

    return AlfaChannel.episodes(item, matches_post=episodesxseason_matches, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()
    
    matches = []
    findS = AHkwargs.get('finds', finds)

    for x, elem_season in enumerate(matches_int):
        #logger.error(elem_season)

        if item.contentSeason != elem_season.get('number', 1): continue
        for elem in elem_season.get('episodes', []):
            elem_json = {}
            #logger.error(elem)

            elem_json['url'] = findS.get('episode_url', '') % (host, elem.get('slug', {}).get('name', ''), 
                                                               item.contentSeason, elem.get('slug', {}).get('episode', 1))
            elem_json['title'] = elem.get('title', '')
            elem_json['season'] = item.contentSeason
            elem_json['episode'] = int(elem.get('number', '1') or '1')
            elem_json['thumbnail'] = elem.get('image', '')

            if not elem_json.get('url', ''): 
                continue

            matches.append(elem_json.copy())

    return matches


# https://embed69.com/cuevana.php?tmdb=755898
# https://embed69.com/gnula.php?tmdb=755898
# https://embed69.com/embed69.php?id=tt0407304  imdb

def findvideos(item):
    logger.info()
    itemlist = [];
    
    data = httptools.downloadpage(host + item.url, canonical=canonical).data
    patron  = '(?ims)type="application/json">(.*?)</script><script'
    match = scrapertools.find_single_match(data, patron)
    json_data = jsontools.load(match)["props"]["pageProps"]["post"]["players"]
    for lang in json_data:
        for info_url in json_data[lang]:
            server = info_url["cyberlocker"]
            if server in list_servers_black: continue
            if server in list_serversx.keys(): server = list_serversx[server]
            qlty = info_url["quality"]
            url = info_url["result"]
            # logger.info("%s %s %s %s" %(lang, server, qlty, url))
            itemlist.append(Item(
                            channel=item.channel,
                            contentTitle=item.contentTitle,
                            contentThumbnail=item.thumbnail,
                            infoLabels=item.infoLabels,
                            language=lang,
                            title='%s' %server,
                            action="play",
                            url=url,
                           ))
    #itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    servers = {'drive': 'gvideo', 'fembed': 'fembed', "player": "oprem", "openplay": "oprem", "embed": "mystream"}

    for lang, elem in list(matches_int.items()):
        #logger.error(elem)

        for link in elem:
            elem_json = {}
            #logger.error(link)

            elem_json['server'] = link.get('cyberlocker', '')
            elem_json['url'] = link.get('result', '')
            elem_json['language'] = '*%s' % lang
            elem_json['quality'] = '*%s' % link.get('quality', '')
            elem_json['title'] = '%s'

            if not elem_json['url']: continue

            if elem_json['server'].lower() in ["waaw", "jetload"]: continue
            if elem_json['server'].lower() in servers:
               elem_json['server'] = servers[elem_json['server'].lower()]

            matches.append(elem_json.copy())

    return matches, langs


def play(item):
    logger.info()
    #item.thumbnail = item.contentThumbnail
    data = httptools.downloadpage(item.url, encoding=encoding).data
    patron = "var url = '([^']+)"
    match = scrapertools.find_single_match(data, patron)
    item.url = match
    return [item]


def search(item, texto, **AHkwargs):
    logger.info()

    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + 'search?q=' + texto

        if texto:
            item.c_type = 'search'
            item.texto = texto
            return list_all(item)
        else:
            return []

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = host + 'archives/movies'

        itemlist = list_all(item)

        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
