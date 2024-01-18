# -*- coding: utf-8 -*-
# -*- Channel PornWorms -*-
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


#      https://www.sexvr.com/  https://celebsnudeworld.com/      https://www.hentaikif.com/  https://www.zigtube.com/   https://www.pornworms.com/

canonical = {
             'channel': 'pornworms', 
             'host': config.get_setting("current_host", 'pornworms', default=''), 
             'host_alt': ["https://www.pornworms.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 10
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []


finds = {'find': {'find_all': [{'tag': ['li'],  'id': re.compile(r"^(?:video|movies)-\d+")}]},
         'categories':  dict([('find', [{'tag': ['ul'], 'class': ['models', 'categories', 'channels']}]),
                             ('find_all', [{'tag': ['a'], 'class': ['thumbnail']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/\d+', '/%s'], ['&page=\d+', '&page=%s']], 
         'last_page': dict([('find', [{'tag': ['div', 'nav', 'ul'], 'class': ['n-pagination', 'pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'href', '@TEXT': '(?:/|=)(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'list_all_stime': dict([('find', [{'tag': ['div', 'span'], 'class': ['video-overlay']}]),
                                                    ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(\d+:\d+(?:\d+|))'}])]),
                            # 'list_all_quality': dict([('find', [{'tag': ['div', 'span'], 'class': ['duration']}]),
                                                      # ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(HD)'}])]),
                            'section_title': dict([('find', [{'tag': ['span', 'div'], 'class':['model-title', 'category-title']}]),
                                                      ('get_text', [{'tag': '', 'strip': True}])]),
                            'section_cantidad': dict([('find', [{'tag': ['span', 'div'], 'class':['model-overlay', 'category-overlay', 'channel-overlay']}]),
                                                      ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(\d+)'}])])
                            },
         'controls': {'url_base64': False, 'cnt_tot': 24, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevo" , action="list_all", url=host + "recent/"))
    itemlist.append(Item(channel=item.channel, title="Mas Visto" , action="list_all", url=host + "viewed/"))
    itemlist.append(Item(channel=item.channel, title="Mejor Valorado" , action="list_all", url=host + "rated/"))
    itemlist.append(Item(channel=item.channel, title="Mas Popular" , action="list_all", url=host + "popular/"))
    itemlist.append(Item(channel=item.channel, title="Mas Favorito" , action="list_all", url=host + "favorited/"))
    itemlist.append(Item(channel=item.channel, title="Mas Comentado" , action="list_all", url=host + "discussed/"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=host + "longest/"))
    itemlist.append(Item(channel=item.channel, title="Mas Descargas" , action="list_all", url=host + "downloaded/"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "pornstar/popular/", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "channels/videos/", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "categories/?o=name", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    # findS['url_replace'] = [['(\/(:?model|movies)\/[^$]+$)', r'\1?o=recent&page=1']]
    if item.extra == 'Canal':
        findS['profile_labels']['section_title'] = {'find': [{'tag': ['img'], '@ARG': 'alt'}]}
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    return AlfaChannel.list_all(item, **kwargs)


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


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
