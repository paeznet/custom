# -*- coding: utf-8 -*-
# -*- Channel LeaksLove -*-
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
             'channel': 'leakslove', 
             'host': config.get_setting("current_host", 'leakslove', default=''), 
             'host_alt': ["https://leakslove.com/"], 
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

finds = {'find': dict([('find', [{'tag': ['div', 'main'], 'id': ['primary', 'main']}]),
                       ('find_all', [{'tag': ['article'], 'class': [re.compile(r"^post-\d+"), 'thumb-block']}])]), 
         'categories':dict([('find', [{'tag': ['div'], 'class': ['videos-list']}]),
                            ('find_all', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}])]), 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': dict([('find', [{'tag': ['div', 'nav'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': 'page/(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['a'], 'class': ['myLink']}]},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'list_all_quality': dict([('find', [{'tag': ['span'], 'class': ['hd-video']}]),
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
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "page/1/?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="list_all", url=host + "page/1/?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=host + "page/1/?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=host + "page/1/?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "actors/page/1/", extra="PornStar"))#¶camgirls/
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "categories/page/1/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:categories|channels|models|pornstars|actor)\/[^$]+$)', r'\1page/1/?filter=latest']]
    
    if item.extra == 'Categorias':
        findS['controls']['cnt_tot'] = 9999
    
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
    itemlist = []
    
    logger.info()
    matches = []
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            elem_json['url'] = elem.get("href", "")
            elem_json['language'] = ''
            
            soup = AlfaChannel.create_soup(item.url, **kwargs)
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
    
    # item.url = "%sbuscar/?q=%s&sort_by=video_viewed&from_videos=1" % (host, texto.replace(" ", "+"))
    item.url = "%s?s=%s&filter=latest" % (host, texto.replace(" ", "+"))
    
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
