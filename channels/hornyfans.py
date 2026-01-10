# -*- coding: utf-8 -*-
# -*- Channel hornyfans -*-
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
             'channel': 'hornyfans', 
             'host': config.get_setting("current_host", 'hornyfans', default=''), 
             'host_alt': ["https://hornysimp.com/"], 
             'host_black_list': [], 
             # 'set_tls': None, 'set_tls_min': False, 'retries_cloudflare': 8, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             # 'cf_assistant': False, 'CF_stat': True, 
             # 'CF': False, 'CF_test': False, 'alfa_s': True
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

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['pt-cv-ifield']}]},     #'id': re.compile(r"^browse_\d+")}]},
         'categories': {'find_all': [{'tag': ['div'], 'class': ['elementor-col-10']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['_page=\d+', '_page=%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pt-cv-pagination-wrapper']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'href', '@TEXT': '_page=(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {},
         'findvideos': dict([('find', [{'tag': ['div'], 'class': 'hscp-video-container'}]),
                             ('find_all', [{'tag': ['iframe'], '@ARG': 'src'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', ''],['View All Post Filed Under ', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'list_all_title': dict([('find', [{'tag': ['h4'], 'class': ['pt-cv-title']}]),
                                                      ('get_text', [{'tag': '', 'strip': True}])]),
                            'section_title': dict([('find', [{'tag': ['h6']}]),
                                                      ('get_text', [{'tag': '', 'strip': True}])]),
                           },
         'controls': {'url_base64': False, 'cnt_tot': 20, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "leaked-clips/?_page=1"))
    itemlist.append(Item(channel=item.channel, title="HD" , action="list_all", url=host + "hd-porns/?_page=1"))
    itemlist.append(Item(channel=item.channel, title="JAV" , action="list_all", url=host + "jav/?_page=1"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "models/", extra="PornStar"))
    # itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['next_page'] = {'find_all': [{'tag': ['a'], 'role': ['button'], '@POS': [-1], '@ARG': 'href'}]}
    findS['controls']['cnt_tot'] = 25
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    findS['controls']['action'] = 'findvideos'
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)
    # return AlfaChannel.list_all(item, **kwargs)


def findvideos(item):
    logger.info()
    
    # return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         # verify_links=False, findvideos_proc=True, **kwargs)
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
            elem_json['server'] =''
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
    
    item.url = "%ssearch/video/?s=%s&o=recent&page=1" % (host, texto.replace(" ", "+"))
    
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
