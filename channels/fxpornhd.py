# -*- coding: utf-8 -*-
# -*- Channel fxpornhd -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

from core import urlparse

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

# https://taboovideosx.com/  https://pornkx.com/   https://taboovideosx.com/

canonical = {
             'channel': 'fxpornhd', 
             'host': config.get_setting("current_host", 'fxpornhd', default=''), 
             'host_alt': ["https://fxpornhd.com/"], 
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
         'categories': {'find_all': [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}]},
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         # 'next_page': dict([('find', [{'tag': ['div', 'ul'], 'class': ['pagination']}]), 
                            # ('find_all', [{'tag': ['a'], '@POS': [-2], '@ARG': 'href'}])]),
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+', '/page/%s']],
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': '(?:/|=)(\d+)'}])]), 
         # 'last_page':  {},
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['div'], 'class': ['video-player-area']}]), 
                             ('find_all', [{'tagOR': ['a'], 'href': True, 'id':"tracking-url"},
                                           {'tag': ['iframe'], 'src': True}])]),
                             
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            # 'list_all_quality': dict([('find', [{'tag': ['div'], 'class': ['b-thumb-item__detail']}]),
                                                      # ('get_text', [{'strip': True}])]),
                            # 'section_cantidad': dict([('find', [{'tag': ['div'], 'class': ['category-videos']}]),
                                                      # ('get_text', [{'strip': True}])])
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
    
    itemlist.append(Item(channel=item.channel, title="fxpornhd" , action="submenu", url= "https://fxpornhd.com/", chanel="fxpornhd", thumbnail = "https://fxpornhd.com/wp-content/uploads/2024/06/logo-fxpornhd.com_.png"))
    itemlist.append(Item(channel=item.channel, title="pornkx" , action="submenu", url= "https://pornkx.com/", chanel="pornkx", thumbnail = "https://pornkx.com/wp-content/uploads/2025/03/logo_kx.png"))
    itemlist.append(Item(channel=item.channel, title="taboovideosx" , action="submenu", url= "https://taboovideosx.com/", chanel="taboovideosx", thumbnail = "https://taboovideosx.com/wp-content/uploads/2023/12/logo-taboo.png"))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    
    config.set_setting("current_host", item.url, item.chanel)
    AlfaChannel.host = item.url
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "page/1/?filter=latest", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="list_all", url=item.url + "page/1/?filter=most-viewed", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "page/1/?filter=popular", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=item.url + "page/1/?filter=longest", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "actors/page/1/", extra="PornStar", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/page/1/", extra="Canal", chanel=item.chanel))
    
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=item.url + "channels/1/", extra="Canal", chanel=item.chanel))
    
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url, chanel=item.chanel))
    
    return itemlist


def section(item):
    logger.info()
    
    return AlfaChannel.section(item, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    
    findS['controls']['action'] = 'findvideos'
    if item.chanel == 'fxpornhd':
        findS['controls']['cnt_tot'] = 25
    
    # return AlfaChannel.list_all(item, finds=findS, **kwargs)
    return AlfaChannel.list_all(item, finds=findS, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.a.get('title', '') \
                                 or elem.find(class_='title').get_text(strip=True) if elem.find(class_='title') else ''
            if not elem_json['title']:
                elem_json['title'] = elem.img.get('alt', '')
            
            if elem.find('video'):
                elem_json['thumbnail'] = elem.video.get('poster', '')
            else:
                elem_json['thumbnail'] = elem.img.get('data-original', '') \
                                         or elem.img.get('data-src', '') \
                                         or elem.img.get('src', '')
            elem_json['stime'] = elem.find(class_='duration').get_text(strip=True) if elem.find(class_='duration') else ''
            if elem.find('span', class_=['hd-video']):
                elem_json['quality'] = elem.find('span', class_=['hd-video']).get_text(strip=True)
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        if not elem_json['url']: continue
        matches.append(elem_json.copy())
    
    return matches


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=False, generictools=True, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            if elem.get("src", ""):
                url = elem.get("src", "")
                if 'php?q=' in url:
                    import base64
                    url = url.split('php?q=')
                    url_decode = base64.b64decode(url[-1]).decode("utf8")
                    url = urlparse.unquote(url_decode)
                    url = scrapertools.find_single_match(url, '<(?:iframe|source) src="([^"]+)"')
                url += "|Referer=%s" % AlfaChannel.host
                elem_json['url'] = url
            else:
                url = elem.get("href", "")
                elem_json['url'] = url
            elem_json['server'] = ''
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
    
    item.url = "%spage/1/?s=%s" % (item.url, texto.replace(" ", "+"))
    
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
