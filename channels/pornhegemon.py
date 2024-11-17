# -*- coding: utf-8 -*-
# -*- Channel PornHegemon -*-
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

####   OUT oct 2024   https://euroxxxvidz.com/

canonical = {
             'channel': 'pornhegemon', 
             'host': config.get_setting("current_host", 'pornhegemon', default=''), 
             'host_alt': ["https://www.pornhegemon.com/"], 
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

finds = {'find': dict([('find', [{'tag': ['main'], 'class': ['site-main']}]),
                       ('find_all', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}])]),
         'categories': dict([('find', [{'tag': ['div'], 'class': ['entry-content']}]),
                             ('find_all', [{'tag': ['h1']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['div'], 'class': ['nav-previous']}, {'tag': ['a'], '@ARG': 'href'}])]),
         'next_page_rgx': [['\/page\/\d+\/', '/page/%s/']], 
         'last_page': {}, 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['div'], 'class': ['entry-content']}]),
                             ('find_all', [{'tag': ['p']}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                           },
         'controls': {'url_base64': False, 'cnt_tot': 30, 'reverse': False, 'profile': 'default'}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel = item.channel, title="Nuevos" , action="list_all", url=host + "page/1/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "categories/", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Region" , action="section", url=host + "categories/", extra="PornStar"))
    itemlist.append(Item(channel = item.channel, title="Categorias" , action="section", url=host + "categories/", extra="Categorias"))
    itemlist.append(Item(channel = item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    # findS['url_replace'] = [['(\/(?:category|channels|models|pornstars)\/[^$]+$)', r'\1page/1/?s']]
    if 'Categorias' in item.extra:
        findS['categories'] = dict([('find', [{'tag': ['li'], 'class': 'menu-item-295'}]), 
                                    ('find_all', [{'tag': ['li']}])])
    elif 'Canal' in item.extra:
        findS['categories'] = dict([('find', [{'tag': ['li'], 'class': 'menu-item-294'}]), 
                                    ('find_all', [{'tag': ['li']}])])
                                    
    else:
        findS['categories'] = dict([('find', [{'tag': ['li'], 'class': 'menu-item-318'}]), 
                                    ('find_all', [{'tag': ['li']}])])
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    findS['controls']['action'] = 'findvideos'
    if "search" in item.c_type:
        findS['profile_labels']['list_all_title'] = dict([('find', [{'tag': ['h2']}]),
                                                          ('get_text', [{'tag': '', 'strip': True}])])
    
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
        #logger.error(elem)
        
        try:
            elem_json['plot']= matches_int[0].text.strip()
            elem_json['url'] = elem.a.get("href", "") if elem.find('a') else elem.iframe.get("src", "")
            elem_json['server'] = ""  
            elem_json['language'] = ''
            if "player.pornhegemon" in elem_json['url']: elem_json['server'] = "netutv"
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
        
        if not elem_json.get('url', ''): continue
        
        matches.append(elem_json.copy())
    
    return matches, langs

def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%spage/1/?s=%s" % (host, texto.replace(" ", "+"))
    
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
