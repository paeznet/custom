# -*- coding: utf-8 -*-
# -*- Channel xorgasmo -*-
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
             'channel': 'xorgasmo', 
             'host': config.get_setting("current_host", 'xorgasmo', default=''), 
             'host_alt': ["https://xorgasmo.com/"], 
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

finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['videos-list']}]),
                       ('find_all', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}])]),
         'categories': dict([('find', [{'tag': ['div'], 'class': ['slider-actors-content']}]),
                             ('find_all', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+', '/page/%s/'], ['&page=\d+', '&page=%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination_custom', 'pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': '(?:/|=)(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'list_all_views': {'find': [{'tag': ['div'], 'class': ['es-porn-icon'], '@ARG': 'class',  '@TEXT': '(es)' }]},
                           },
         'controls': {'url_base64': False, 'cnt_tot': 30, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "videos/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistos" , action="list_all", url=host + "most-viewed/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=host + "most-liked/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Favoritos" , action="list_all", url=host + "recomended/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=host + "longest/page/1/"))
    itemlist.append(Item(channel=item.channel, title="2024" , action="list_all", url=host + "2024/page/1/?f=p1"))
    itemlist.append(Item(channel=item.channel, title="2023" , action="list_all", url=host + "2023/page/1/?f=p1"))
    itemlist.append(Item(channel=item.channel, title="2022" , action="list_all", url=host + "2022/page/1/?f=p1"))
    itemlist.append(Item(channel=item.channel, title="2021" , action="list_all", url=host + "2021/page/1/?f=p1"))
    itemlist.append(Item(channel=item.channel, title="2020" , action="list_all", url=host + "2020/page/1/?f=p1"))
    itemlist.append(Item(channel=item.channel, title="2019" , action="list_all", url=host + "2019/page/1/?f=p1"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "channels/page/1/", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "pornstar/page/1/", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "categorias/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    # findS['url_replace'] = [['(\/(?:categories|channels|models|pornstars)\/[^$]+$)', r'\1?sort_by=post_date&from=1']]
    if item.extra == 'PornStar':
        findS['controls']['cnt_tot'] = 28
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    if item.extra:
        findS['controls']['cnt_tot'] = 24
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    item.extra = "Search"
    item.url = "%ssearch/%s/page/1/?f=new" % (host, texto.replace(" ", "+"))
    
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
