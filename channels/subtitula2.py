# -*- coding: utf-8 -*-
# -*- Channel subtitula2 -*-
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

######    FALTA SERVER  https://iplayerhls.com/e/e9za2emfxkq2

canonical = {
             'channel': 'subtitula2', 
             'host': config.get_setting("current_host", 'subtitula2', default=''), 
             'host_alt': ["https://pornosubtitula2.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
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

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['video-block']}]},     #             'id': re.compile(r"^browse_\d+")}]},
         'categories': {'find_all': [{'tag': ['div'], 'class': ['video-block']}]},
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s'], ['&page=\d+', '&page=%s']], 
         'last_page': dict([('find', [{'tag': ['div','ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], '@ARG': 'href', '@TEXT': '/page/(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['iframe']}]},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', ''], ['(?i)View all post filed under ', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'list_all_premium': {'find': [{'tag': ['img'], 'class': ['premium-vip2'], '@ARG': 'class',  '@TEXT': '(premium)' }]}
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
    
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=host + "page/1/?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas vistas" , action="list_all", url=host + "page/1/?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mas populares" , action="list_all", url=host + "page/1/?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas larga" , action="list_all", url=host + "page/1/?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "categorias/page/1/", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "actrices/", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "tags/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    if item.extra == 'Categorias':
        findS['categories'] =  {'find_all': [{'tag': ['div'], 'class': ['tag-item']}]}
        findS['profile_labels']['section_title'] = dict([('find', [{'tag': ['a']}]),
                                                         ('get_text', [{'tag': '', 'strip': True}])])

    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    findS['controls']['action'] = 'findvideos'
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


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
    
    soup = AHkwargs.get('soup', {})
    
    if soup.find_all('a', href=re.compile("/actor/[A-z0-9-]+/")):
        pornstars = soup.find_all('a', href=re.compile("/actor/[A-z0-9-]+/"))
        
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        item.plot = pornstar
        # lista = item.contentTitle.split('[/COLOR]')
        # pornstar = pornstar.replace('[/COLOR]', '')
        # pornstar = ' %s' %pornstar
        # if AlfaChannel.color_setting.get('quality', '') in item.contentTitle:
            # lista.insert (2, pornstar)
        # else:
            # lista.insert (1, pornstar)
        # item.contentTitle = '[/COLOR]'.join(lista)
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            if elem.get("data-litespeed-src", ""):
                elem_json['url'] = elem['data-litespeed-src']
            else:
                elem_json['url'] = elem['src']
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
    
    item.url = "%spage/1/?s=%s&filter=latest" % (item.url, texto.replace(" ", "+"))
    
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
