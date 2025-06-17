# -*- coding: utf-8 -*-
# -*- Channel LovingSiren -*-
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

canonical = {
             'channel': 'lovingsiren', 
             'host': config.get_setting("current_host", 'lovingsiren', default=''), 
             'host_alt': ["https://lovingsiren.com/"], 
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

finds = {'find':  dict([('find', [{'tag': ['div', 'main'], 'id': ['primary', 'main']}]),
                       ('find_all', [{'tag': ['article'], 'class': [re.compile(r"^post-\d+")]}])]),      #'id': re.compile(r"^browse_\d+")}]},
         'categories':  dict([('find', [{'tag': ['div', 'main'], 'id': ['primary', 'main']}]),
                              ('find_all', [{'tag': ['article'], 'class': [re.compile(r"^post-\d+")]}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': '(?:/|=)(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['div'], 'class': ['responsive-player', 'awpcontenedor']}]},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            # 'list_all_title': dict([('find', [{'tag': ['h3']}]),
                                                    # ('get_text', [{'tag': '', 'strip': True}])])
                           },
         'controls': {'url_base64': False, 'cnt_tot': 28, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)

def mainlist(item):
    logger.info()
    itemlist = []
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "page/1/?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas visto" , action="list_all", url=host + "page/1/?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="list_all", url=host + "page/1/?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=host + "page/1/?filter=longest"))
    # itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "page/1/?filter=latest"))
    # itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "page/1/?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Bangbros" , action="list_all", url=host + "category/bangbros/page/1"))
    itemlist.append(Item(channel=item.channel, title="Brazzers" , action="list_all", url=host + "category/brazzers/page/1"))
    itemlist.append(Item(channel=item.channel, title="Putalocura" , action="list_all", url=host + "category/putalocura/page/1"))
    itemlist.append(Item(channel=item.channel, title="SexMex" , action="list_all", url=host + "category/sexmex/page/1"))
    itemlist.append(Item(channel=item.channel, title="MilkyPeru" , action="list_all", url=host + "category/milkyperu/page/1"))
    itemlist.append(Item(channel=item.channel, title="Onlyfans" , action="list_all", url=host + "category/onlyfans/page/1"))
    itemlist.append(Item(channel=item.channel, title="18-years-old" , action="list_all", url=host + "category/18-years-old/page/1"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "actors/page/1/", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    findS = finds.copy()
    if item.extra == 'PornStar':
        findS['controls']['cnt_tot'] = 20
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
    # logger.debug(matches_int)
    for elem in matches_int:
        elem_json = {}
        
        try:
            if elem.find('iframe'):
                elem_json['url'] = elem.iframe.get("data-src", "") or elem.iframe.get('src', '')
            else:
                continue
            if ".realsrv." in elem_json['url']: continue
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
