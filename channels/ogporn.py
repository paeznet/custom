# -*- coding: utf-8 -*-
# -*- Channel OGporn -*-
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
             'channel': 'ogporn', 
             'host': config.get_setting("current_host", 'ogporn', default=''), 
             'host_alt': ["https://ogporn.com/"], 
             'host_black_list': [], 
             'set_tls': None, 'set_tls_min': False, 'retries_cloudflare': 5, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'cf_assistant': False, 'CF_stat': True, 
             'CF': False, 'CF_test': False, 'alfa_s': True
             # 'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             # 'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []

finds = {'find': {'find_all': [{'tag': ['a'], 'class': ['video']}]},     #'id': re.compile(r"^browse_\d+")}]},
         'categories': {'find_all': [{'tag': ['a'], 'class': ['taxonomy-link']}]},
                       # dict([('find', [{'tag': ['div'], 'class': ['catg', 'series', 'models']}]),
                             # ('find_all', [{'tag': ['a']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         # 'next_page': {},
         # 'next_page': dict([('find', [{'tag': ['div'], 'class': ['pagination-page-bas']}, {'tag': ['span']}]),
                            # ('find_next_sibling', [{'tag': ['a'], '@ARG': 'href'}])]), 
         'next_page': dict([('find', [{'tag': ['div'], 'class': ['nav-previous']}, {'tag': ['a'], '@ARG': 'href'}])]),
         'next_page_rgx': [['\/\d+', '/%s'], ['&page=\d+', '&page=%s']], 
         # 'last_page': dict([('find', [{'tag': ['ul', 'div'], 'class': ['nav-previous']}]), 
                            # ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           # '@ARG': 'href', '@TEXT': '(?:/|=)(\d+)'}])]), 
         'last_page': {},
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
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
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "series/", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "model/", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "categories/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    return itemlist


def section(item):
    logger.info()
    
    return AlfaChannel.section(item, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            
            elem_json['url'] = elem.get('href', '')
            elem_json['title'] = elem.get('title', '') \
                                 or elem.h2.get_text(strip=True)
            elem_json['thumbnail'] = ""
            
            if elem.find('span', class_=['taxonomy-count']):
                elem_json['cantidad'] = elem.find('span', class_=['taxonomy-count']).get_text(strip=True)
            if elem.find('total'):
                elem_json['cantidad'] = elem.total.get_text(strip=True)
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        if not elem_json['url']: continue
        matches.append(elem_json.copy())
    
    return matches


def list_all(item):
    logger.info()
    
    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            if elem.find('span', class_=re.compile(r"^home-\w+")): continue
            
            elem_json['url'] = elem.get('href', '')
            elem_json['title'] = elem.get('title', '')
            elem_json['thumbnail'] = elem.get('data-bg', '')
            
            elem_json['stime'] = elem.find(class_='time').get_text(strip=True) if elem.find(class_='time') else ''
            
            if elem.find('strong'):
                elem_json['canal'] = elem.find('strong').get_text(strip=True)
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        if not elem_json['url']: continue
        matches.append(elem_json.copy())
    
    return matches


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def play(item):
    logger.info()
    itemlist = []
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    
    if soup.find('div', class_="model-list"):
        pornstars = soup.find('div', class_="model-list").find_all('a', href=re.compile("/model/[A-z0-9-]+/"))
        
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s' %pornstar
        if AlfaChannel.color_setting.get('tvshow', '') in item.contentTitle:
            lista.insert (2, pornstar)
        else:
            lista.insert (1, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


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
