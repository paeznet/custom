# -*- coding: utf-8 -*-
# -*- Channel xfuntaxy -*-
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

IDIOMAS = AlfaChannelHelper.IDIOMAS_A
list_language = list(set(IDIOMAS.values()))
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES_A
list_quality_tvshow = []
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS_A

forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'xfuntaxy', 
             'host': config.get_setting("current_host", 'xfuntaxy', default=''), 
             'host_alt': ["https://xfuntaxy.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
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

finds = {'find': dict([('find', [{'tag': ['main'], 'id': ['main']}]),
                       ('find_all', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}])]),
         'categories': dict([('find', [{'tag': ['div'], 'class': ['videos-list']}]),
                             ('find_all', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+\/', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': 'page/(\d+)'}])]), 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['header'], 'class': ['entry-header']}]), 
                             ('find_all', [{'tagOR': ['a'], 'href': True, 'id': 'tracking-url'},
                                           {'tag': ['meta'], 'content': True, 'itemprop': 'embedURL'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'controls': {'url_base64': False, 'cnt_tot': 32, 'reverse': False, 'profile': 'default'}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel = item.channel, title="Peliculas" , action="list_all", url=host + "category/full-movies/page/1/?filter=latest"))
    itemlist.append(Item(channel = item.channel, title="Nuevos" , action="list_all", url=host + "page1/?filter=latest"))
    itemlist.append(Item(channel = item.channel, title="Mas vistos" , action="list_all", url=host + "page1/?filter=most-viewed"))
    itemlist.append(Item(channel = item.channel, title="Mejor valorado" , action="list_all", url=host + "page1/?filter=popular"))
    itemlist.append(Item(channel = item.channel, title="Mas metraje" , action="list_all", url=host + "page1/?filter=longest"))
    itemlist.append(Item(channel = item.channel, title="Canal" , action="section", url=host + "categories/page/1/", extra="Canal"))
    itemlist.append(Item(channel = item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    if item.extra:
        findS['controls']['cnt_tot'] = 50
    
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
    
    soup = AHkwargs.get('soup', {})
    
    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            if isinstance(elem, str):
                elem_json['url'] = elem
                if elem_json['url'].endswith('.jpg'): continue
            else:
                elem_json['url'] = elem.get("href", "") or elem.get("content", "")
            elem_json['language'] = ''
            
            
            pornstars = soup.find_all('a', href=re.compile(r"/(?:cast|pornstar|actor)/[A-z0-9-]+"))
            if pornstars:
                for x, value in enumerate(pornstars):
                    pornstars[x] = value.get_text(strip=True)
                pornstar = '& '.join(pornstars)
                # pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
                elem_json['plot'] = pornstar
            
            
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())

        if not elem_json.get('url', ''): continue

        matches.append(elem_json.copy())

    return matches, langs


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%spage/1/?s=%s&filter=latest" % (host, texto.replace(" ", "+"))
    
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