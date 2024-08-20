# -*- coding: utf-8 -*-
# -*- Channel 24xxx -*-
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
             'channel': '24xxx', 
             'host': config.get_setting("current_host", '24xxx', default=''), 
             'host_alt': ["https://www.24xxx.porn/"], 
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

finds = {'find': dict([('find', [{'tag': ['ul'], 'class': ['production-block__list']}]),
                       ('find_all', [{'tag': ['li']}])]),
         'categories': dict([('find', [{'tag': ['ul'], 'class': ['models-block__list']}]),
                             ('find_all', [{'tag': ['li']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['_page-\d+', '_page-%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination-block']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'href', '@TEXT': 'page-(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'list_all_stime': {'find': [{'tag': ['span'], 'class': ['vtime'], '@TEXT': '(\d+:\d+)' }]},
                            'list_all_quality': dict([('find', [{'tag': ['div'], 'class': ['hd']}]),
                                                      ('get_text', [{'tag': '', 'strip': True}])])
                           },
         'controls': {'url_base64': False, 'cnt_tot': 52, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "videos/new_page-1.html"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistos" , action="list_all", url=host + "videos/top_page-1.html"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=host + "videos/top100_page-1.html"))
    itemlist.append(Item(channel=item.channel, title="Mas Comentado" , action="list_all", url=host + "videos/commented_page-1.html"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=host + "videos/time_page-1.html"))
    itemlist.append(Item(channel=item.channel, title="HD" , action="list_all", url=host + "videos/hd_page-1.html"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "models/page-1.html", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host , extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    
    if item.extra == 'Categorias':
        findS['categories'] =  dict([('find', [{'tag': ['ul'], 'class': ['categories__list']}]),
                                     ('find_all', [{'tag': ['li']}])])
        findS['last_page'] = {}
        findS['next_page'] = dict([('find', [{'tag': ['div'], 'class': ['pagination-block']}]), 
                                   ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]) 

    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    
    if item.extra == 'PornStar':
        findS['controls']['cnt_tot'] = 100
    
    if item.extra == 'Categorias':
        findS['controls']['cnt_tot'] = 44
        findS['last_page'] = {}
        findS['next_page'] = dict([('find', [{'tag': ['div'], 'class': ['pagination-block']}]), 
                                   ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]) 
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def play(item):
    logger.info()
    itemlist = []
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    data = soup.find('script', type='text/javascript').string
    matches = scrapertools.find_single_match(data, 'var file = "([^"]+)"')
    matches = matches.split(",")
    for elem in matches:
        elem =elem.split("]./")
        quality = scrapertools.find_single_match(elem[0], '(\d+)p')
        url = elem[-1]
        url = AlfaChannel.urljoin(host,url)
        itemlist.append(['[24xxx] .mp4 %sp' %quality, url])
    itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/%s/" % (host, texto.replace(" ", "-"))
    
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
