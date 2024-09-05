# -*- coding: utf-8 -*-
# -*- Channel draftsex -*-
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

# https://pornenix.com/     https://playenix.com/
# https:/daftsex.app/   https://draftsex.porn/

canonical = {
             'channel': 'draftsex', 
             'host': config.get_setting("current_host", 'draftsex', default=''), 
             'host_alt': ["https://draftsex.porn/"], 
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

finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['box__bd']}]),
                       ('find_all', [{'tag': ['div'], 'class': ['item']}])]),    #'id': re.compile(r"^browse_\d+")}]},
         'categories': {'find_all': [{'tag': ['div'], 'class': ['mitem', 'citem']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['a'], 'class': ['-next'], '@ARG': 'href'}])]), 
         'next_page_rgx': [['page\d+.html', 'next_page_url']], 
         'last_page': {},
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'list_all_stime': {'find': [{'tag': ['span'], 'class': ['-duration'], '@TEXT': '(\d+:\d+)' }]},
                           },
         'controls': {'url_base64': False, 'cnt_tot': 36, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "most-recent/"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistos" , action="list_all", url=host + "most-viewed/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=host + "top-rated/"))
    itemlist.append(Item(channel=item.channel, title="Mas Comentado" , action="list_all", url=host + "most-discussed/"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=host + "longest/"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=host + "models/rating/page1.html", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "channels/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:channels)\/[^$]+$)', r'\1page1.html']]
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    findS = finds.copy()
    
    if "/models/" in item.url:
        findS['find'] = dict([('find', [{'tag': ['section'], 'class': ['-sec-profile']}]),
                              ('find_all', [{'tag': ['div'], 'class': ['item']}])])
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/%s/newest/page1.html" % (host, texto.replace(" ", "-"))
    
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
