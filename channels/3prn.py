# -*- coding: utf-8 -*-
# -*- Channel 3prn -*-
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
             'channel': '3prn', 
             'host': config.get_setting("current_host", '3prn', default=''), 
             'host_alt': ["https://3prn.com/"], 
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

finds = {'find':  dict([('find', [{'tag': ['div'], 'class': ['thumbs-items']}]),
                       ('find_all', [{'tag': ['div'], 'class': ['thumb']}])]),
         'categories': dict([('find', [{'tag': ['div'], 'class': ['thumbs-items']}]),
                             ('find_all', [{'tag': ['li'], 'class': ['thumb']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['/\?from2=\d+', '/?from2=%s'], ['\/\d+\/', '/%s/']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'href', '@TEXT': '/(\d+)/'}])]), 
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'section_title': dict([('find', [{'tag': ['span', 'div'], 'class': ['title']}]),
                                                      ('get_text', [{'tag': '', 'strip': True}])]),
                            'section_cantidad': dict([('find', [{'tag': ['div'], 'class': ['duration']}]),
                                                      ('get_text', [{'tag': '', 'strip': True}])])
                            },
         'controls': {'url_base64': False, 'cnt_tot': 32, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=host + "1/"))
    itemlist.append(Item(channel=item.channel, title="Mejor Valorada" , action="list_all", url=host + "top-rated/1/"))
    itemlist.append(Item(channel=item.channel, title="Mas Largas" , action="list_all", url=host + "longest/1/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "categories/1/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    if item.extra == 'Categorias':
        findS['controls']['cnt_tot'] = 9999
        # findS['url_replace'] = [['($)', '1/']]
        # findS['url_replace'] = [['(\/(?:categories|channels|models)\/[^$]+$)', r'\1?sort_by=post_date&from=1']]
        # findS['next_page'] = dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                                   # ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]) 

    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    if "search" in item.c_type:
        findS['controls']['cnt_tot'] = 12
        findS['find'] = {'find_all': [{'tag': ['div'], 'class': ['thumb']}]}
        findS['last_page'] = {'find': [{'tag': ['div'], 'class': ['show-more'], '@ARG': 'data-total'}]}
    if item.extra == 'Categorias':
        findS['next_page'] = dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
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
    if soup.find_all('a', href=re.compile("/models/[A-z0-9-]+/")):
        pornstars = soup.find_all('a', href=re.compile("/models/[A-z0-9-]+/"))
        logger.debug(pornstars)
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s' %pornstar
        if "HD" in item.contentTitle:
            lista.insert (2, pornstar)
        else:
            lista.insert (1, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)
    
    if soup.find('div', class_='embed-wrap'):
        url = soup.find('div', class_='embed-wrap').iframe['src']
    else:
        url = item.url
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/%s/?from2=1" % (host, texto.replace(" ", "+"))
    
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
