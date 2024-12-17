# -*- coding: utf-8 -*-
# -*- Channel GotAnyNudes -*-
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
             'channel': 'gotanynudes', 
             'host': config.get_setting("current_host", 'gotanynudes', default=''), 
             'host_alt': ["https://gotanynudes.com/"], 
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


finds = {'find': {'find_all': [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}]},
         'categories': dict([('find', [{'tag': ['div'], 'id': ['primary']}]),
                             ('find_all', [{'tag': ['a']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['a'], 'class': ['g1-load-more'],
                             '@ARG': 'data-g1-next-page-url'}])]), 
         'next_page_rgx': [['&page=\d+', '&page=%s'], ['\/\d+', '/%s']], 
         'last_page': {},
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                           },
         'controls': {'url_base64': False, 'cnt_tot': 11, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "page/1/?order=newest"))
    # itemlist.append(Item(channel=item.channel, title="Mas Vistos" , action="list_all", url=host + "page/1/?order=most_views"))
    # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=host + "page/1/?order=most_shares"))
    # itemlist.append(Item(channel=item.channel, title="Mas antiguo" , action="list_all", url=host + "page/1/?order=oldest"))
    # itemlist.append(Item(channel=item.channel, title="Mas Comentado" , action="list_all", url=host + "page/1/?order=most_commented"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "a-z-leaked-model-database-list-mtg-4", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "categories/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    # findS['url_replace'] = [['(\/(?:categories|channels|models|pornstars)\/[^$]+$)', r'\1?sort_by=post_date&from=1']]
    
    if item.extra == 'PornStar':
        findS['controls']['cnt_tot'] = 48
        if "a-z-leaked-model" in item.url:
            soup = AlfaChannel.create_soup(item.url, **kwargs)
            data = soup.find('script', id='custom-gallery-js-extra').string
            nonce = scrapertools.find_single_match(data, '"nonce":"([^"]+)"')
            last = scrapertools.find_single_match(data, '"max_pages":"(\d+)"')
            item.post = 'action=load_more&nonce=%s&page=1' %nonce
            item.last_page = last
        item.url = AlfaChannel.doo_url
        findS['categories'] = {'find_all': [{'tag': ['a'], 'class': ['profile']}]}
        findS['next_page'] = {}
         
    if item.extra == 'Categorias':
        findS['profile_labels']['section_thumbnail'] = {'find': [{'tag': ['img'], '@ARG': 'data-lazy-src'}]}
    
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
