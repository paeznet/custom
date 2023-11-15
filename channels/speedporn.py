# -*- coding: utf-8 -*-
# -*- Channel Speedporn -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

from lib import AlfaChannelHelper
if not PY3: _dict = dict; from AlfaChannelHelper import dict
from AlfaChannelHelper import DictionaryAdultChannel
from AlfaChannelHelper import re, traceback, time, base64, xbmcgui
from AlfaChannelHelper import Item, servertools, scrapertools, jsontools, get_thumb, config, logger, filtertools, autoplay

IDIOMAS = {}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = []
list_quality_tvshow = []
list_servers = []
forced_proxy_opt = 'ProxySSL'

# https://xxxscenes.net  https://www.netflixporno.net   https://mangoporn.net   https://speedporn.net

canonical = {
             'channel': 'speedporn', 
             'host': config.get_setting("current_host", 'speedporn', default=''), 
             'host_alt': ["https://speedporn.net/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['video-block']}]},     #             'id': re.compile(r"^browse_\d+")}]},
         'categories': {'find_all': [{'tag': ['div'], 'class': ['video-block']}]},
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '\/page\/%s'], ['&page=\d+', '&page=%s']], 
         'last_page': dict([('find', [{'tag': ['div','ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], '@ARG': 'href', '@TEXT': '/page/(\d+)'}])]), 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['div'], 'id': 'pettabs'}]),
                             ('find_all', [{'tag': ['a'], '@ARG': 'href'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', ''], ['(?i)View all post filed under ', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                           },
         'controls': {'url_base64': False, 'cnt_tot': 49, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=host + "category/porn-movies/page/1/?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas vistas" , action="list_all", url=host + "category/porn-movies/page/1/?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mas populares" , action="list_all", url=host + "category/porn-movies/page/1/?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas larga" , action="list_all", url=host + "category/porn-movies/page/1/?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="Año" , action="section", url=host + "releasing-years/" , extra="Año"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "all-porn-movie-studios/" , extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "pornstars/", extra="PornStar"))
    # itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "genres/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host))
    
    itemlist.append(Item(channel=item.channel, title="-----------------------------------------------" ))
    itemlist.append(Item(channel=item.channel, title="Videos" , action="submenu", url=host + "xxxfree/"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "page/1/?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas visto" , action="list_all", url=item.url + "page/1/?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mas popular" , action="list_all", url=item.url + "page/1/?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=item.url + "page/1/?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="Año" , action="section",url=item.url +"releasing-years/", extra="Año"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=item.url + "studios/" , extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=item.url + "pornstars/", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "genres/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search",url=item.url))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    if item.extra == 'Canal':
        findS['categories'] =  {'find_all': [{'tag': ['div'], 'class': ['tag-item']}]}
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    findS['controls']['action'] = 'findvideos'
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=False, generictools=True, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            elem_json['url'] = elem
            elem_json['language'] = ''
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
        
        if not elem_json.get('url', ''): continue
        matches.append(elem_json.copy())
    
    return matches, langs


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%spage/1/?s=%s" % (item.url, texto.replace(" ", "+"))
    
    try:
        if texto:
            item.c_type = "search"
            item.texto = texto
            return list_all(item)
        else:
            return []
    
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
