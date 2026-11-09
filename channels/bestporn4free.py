# -*- coding: utf-8 -*-
# -*- Channel BestPorn4Free -*-
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
forced_proxy_opt = ''

canonical = {
             'channel': 'bestporn4free', 
             'host': config.get_setting("current_host", 'bestporn4free', default=''), 
             'host_alt': ["https://bestporn4free.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 20
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []


finds = {'find': dict([('find', [{'tag': ['main'], 'id': ['main']}]),
                       ('find_all', [{'tag': ['article'], 'class': [re.compile(r'loop-video')]}])]),
         'categories': dict([('find', [{'tag': ['ul'], 'class': ['wp-block-categories-list']}]),
                             ('find_all', [{'tag': ['a'], 'href': re.compile(r'/category/')}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [[r'/page/\d+', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], 'string': ['Last'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': r'/page/(\d+)'}])]), 
         'plot': {}, 
         'findvideos': dict([('find_all', [{'tag': ['iframe']}])]),
         'title_clean': [], 
         'quality_clean': [], 
         'url_replace': [], 
         'profile_labels': {},
         'controls': {'url_base64': False, 'cnt_tot': 20, 'reverse': False, 'profile': 'default'},
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistos" , action="list_all", url=host + "?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Populares" , action="list_all", url=host + "?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas Largos" , action="list_all", url=host + "?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host, extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    
    return AlfaChannel.section(item, **kwargs)


def list_all(item):
    logger.info()
    
    return AlfaChannel.list_all(item, postprocess=list_all_postprocess, **kwargs)


def list_all_postprocess(elem, new_item, item, **AHkwargs):
    # La portada mete un post fijo de publicidad ("More Premium XXX Videos Click Here") entre las fichas.
    if 'more-premium' in new_item.url:
        return None
    
    return new_item


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%s?s=%s" % (host, texto.strip().replace(" ", "+"))
    
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
