# -*- coding: utf-8 -*-
# -*- Channel FlyFLV -*-
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
             'channel': 'flyflv', 
             'host': config.get_setting("current_host", 'flyflv', default=''), 
             'host_alt': ["https://www.flyflv.com/"], 
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

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['movieThumb']}]},     #'id': re.compile(r"^browse_\d+")}]},
         'categories': {'find_all': [{'tag': ['div'], 'class': ['modelThumb', 'movieThumb']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/\d+$', '/%s'], ['\/\d+\?', '/%s?']], 
         'last_page': dict([('find', [{'tag': ['ul'], 'class': ['pages','pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': '(?:\/|=)(\d+)(?:\?|$)'}])]), 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['li'], 'class': 'link-tabs-container', '@ARG': 'href'}]),
                             ('find_all', [{'tag': ['a'], '@ARG': 'href'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                           },
         'controls': {'url_base64': False, 'cnt_tot': 26, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "1", orientation=1))
    itemlist.append(Item(channel=item.channel, title="Mas Vistos" , action="list_all", url=host + "1?sort=popularity", orientation=1))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=host + "1?sort=duration.desc", orientation=1))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "paysites/1", extra="Canal", chanel=item.chanel, orientation=1))
    itemlist.append(Item(channel=item.channel, title="Pornstar" , action="section", url=host + "models/1", extra="PornStar", chanel=item.chanel, orientation=1))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host, extra="Categorias", orientation=1))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host, orientation=1))
    
    itemlist.append(Item(channel = item.channel, title = ""))
    
    itemlist.append(Item(channel=item.channel, title="Trans", action="submenu", url=host + "shemale/", orientation=3))
    itemlist.append(Item(channel=item.channel, title="Gay", action="submenu", url=host + "gay/", orientation=2))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    
    kwargs['headers'] = {'Referer': host, "Cookie": "contentNiche=%s" % item.orientation}
    
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=item.url + "1?sort=addDate.desc", orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="list_all", url=item.url + "1?sort=popularity", orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="Mas Largas" , action="list_all", url=item.url + "1?sort=duration.desc", orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="Sitios" , action="section", url=item.url + "paysites/1", extra="Canal", orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=item.url + "models/1", extra="PornStar", orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url, extra="Categorias", orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="Buscar", url=item.url, action="search", orientation=item.orientation))
    return itemlist


def section(item):
    logger.info()
    findS = finds.copy()
    
    findS['url_replace'] = [['\?sort\=popularity', ''],['($)', '/1?sort=addDate.desc']]
    if item.extra == 'Categorias':
        findS['url_replace'] = [['($)', '&sort=addDate.desc'],['shemale', 'shemale/'],['gay', 'gay/'],['\?q=', '1?q=']]

        findS['categories'] = dict([('find', [{'tag': ['ul'], 'class': ['categories']}]), 
                                    ('find_all', [{'tag': ['li']}])])
        findS['profile_labels']['section_cantidad'] = dict([('find', [{'tag': ['p']}]),
                                                            ('get_text', [{'strip': True}])])
    kwargs['headers'] = {'Referer': host, "Cookie": "contentNiche=%s" % item.orientation}
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    kwargs['headers'] = {'Referer': host, "Cookie": "contentNiche=%s" % item.orientation}
    
    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        try:
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.a.get('title', '') \
                                 or elem.find(class_='thumbDesc').get_text(strip=True) if elem.find(class_='thumbDesc') else ''
            if not elem_json['title']:
                elem_json['title'] = elem.img.get('alt', '')
            elem_json['thumbnail'] = elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') \
                                     or elem.video.get('poster', '') \
                                     or elem.img.get('src', '')
            # elem_json['stime'] = elem.find(class_='movieTime').get_text(strip=True) if elem.find(class_='movieTime') else ''
            if elem.find('span', class_=['thumb__bage']):
                elem_json['quality'] = elem.find('span', class_=['thumb__bage']).get_text(strip=True)
            
            paysite = ""
            network = ""
            if elem.find('a', href=re.compile("movies/networks/[0-9-]+/")):
                network = elem.find('a', href=re.compile("movies/networks/[0-9-]+/")).get_text(strip=True)
            if elem.find_all('a', href=re.compile("movies/paysites/[0-9-]+/")):
                paysite = elem.find('a', href=re.compile("movies/paysites/[0-9-]+/")).get_text(strip=True)
            if network in paysite:
                network = ""
            elem_json['canal'] = "%s %s" %(network, paysite)
            
            pornstars = elem.find_all('a', href=re.compile("movies/models/[0-9-]+/"))
            if pornstars:
                for x, value in enumerate(pornstars):
                    pornstars[x] = value.get_text(strip=True)
                elem_json['star'] = ' & '.join(pornstars)
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


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%s1?q=%s&sort=addDate.desc" % (item.url, texto.replace(" ", "+"))
    
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
