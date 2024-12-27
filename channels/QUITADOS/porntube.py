# -*- coding: utf-8 -*-
# -*- Channel PornTube -*-
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

#  https://www.porntube.com    https://www.pornerbros.com   https://www.4tube.com  https://www.fux.com
canonical = {
             'channel': 'porntube', 
             'host': config.get_setting("current_host", 'porntube', default=''), 
             'host_alt': ["https://www.porntube.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
url_api = "%sapi/video/list?order=%s&orientation=%s&p=1&ssr=false"

timeout = 5
kwargs = {}
kwargs['soup'] = False
kwargs['json'] = True
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []

finds = {'find': {},
         'categories': {}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['&p=\d+', '&p=%s']], 
         'last_page': {}, 
         'plot': {}, 
         'findvideos': {}, 
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''], ['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'controls': {'url_base64': False, 'cnt_tot': 16, 'reverse': False}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)

def mainlist(item):
    logger.info()
    itemlist = []
    soup = AlfaChannel.create_soup(host, alfa_s=True) #Para coger canonical
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=url_api % (host, "date", "straight")))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="list_all", url=url_api %  (host, "views", "straight")))
    itemlist.append(Item(channel=item.channel, title="Mas Valorada" , action="list_all", url=url_api %  (host, "rating", "straight")))
    itemlist.append(Item(channel=item.channel, title="Longitud" , action="list_all", url=url_api %  (host, "duration", "straight")))
    itemlist.append(Item(channel=item.channel, title="PornStars" , action="section", url=host + "api/pornstar/list?order=videos&orientation=straight&p=1&ssr=false", extra="PornStars"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "api/channel/list?order=rating&orientation=straight&p=1&ssr=false", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Categorías" , action="section", url=host + "api/tag/list?orientation=straight&ssr=false", extra="Categorías"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", orientation= "straight"))
    
    itemlist.append(Item(channel=item.channel, title="", action="", folder=False))
    
    itemlist.append(Item(channel=item.channel, title="Trans", action="submenu", orientation="shemale"))
    itemlist.append(Item(channel=item.channel, title="Gay", action="submenu", orientation="gay"))
    
    return itemlist


def submenu(item):
    logger.info()
    
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=url_api % (host, "date", item.orientation), orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="list_all", url=url_api %  (host, "views", item.orientation), orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="Mas Valorada" , action="list_all", url=url_api %  (host, "rating", item.orientation), orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="Longitud" , action="list_all", url=url_api %  (host, "duration", item.orientation), orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="PornStars" , action="section", url=host + "api/pornstar/list?order=videos&orientation=%s&p=1&ssr=false" % item.orientation, orientation=item.orientation, extra="PornStars"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "api/channel/list?order=rating&orientation=%s&p=1&ssr=false" % item.orientation, orientation=item.orientation, extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Categorías" , action="section", url=host + "api/tag/list?orientation=%s&ssr=false" % item.orientation, orientation=item.orientation, extra="Categorías"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", orientation=item.orientation))
    
    return itemlist


def section(item):
    logger.info()
    
    return AlfaChannel.section(item, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()
    
    matches = []
    findS = AHkwargs.get('finds', finds)
    
    if matches_int.get('tags', {}): 
        matches_int = matches_int.get('tags', {}).copy()
        c_type = 'tags'
    elif matches_int.get('channels', {}): 
        matches_int = matches_int.get('channels', {}).copy()
        c_type = 'channels'
    elif matches_int.get('pornstars', {}): 
        matches_int = matches_int.get('pornstars', {}).copy()
        c_type = 'pornstars'
    if not matches_int: return matches
    
    if matches_int.get('pages'): AlfaChannel.last_page = matches_int.get('pages', 0)
    if matches_int.get('limit'): AlfaChannel.finds['controls']['cnt_tot'] = matches_int.get('limit', findS['controls']['cnt_tot'])
    
    matches_int = matches_int.get("_embedded", {}).get("items", {})
    if not matches_int: return matches
    
    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)
        
        try:
            elem_json['url'] = "%sapi/%s/%s?order=%s&orientation=%s&p=1&ssr=false" \
                                % (host, c_type, elem.get('slug', ''), "date", item.orientation)
            elem_json['title'] = elem.get('name', '')
            elem_json['thumbnail'] = elem.get('thumbDesktop', '') or elem.get('thumbUrl', '')
            elem_json['cantidad'] = elem.get('videoCount', '')
        
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
    
    if matches_int.get('embedded', {}).get('videos', {}): matches_int = matches_int['embedded'].copy()
    matches_int = matches_int.get('videos', {}).copy()
    if not matches_int: return matches
    
    if matches_int.get('pages'): AlfaChannel.last_page = matches_int.get('pages', 0)
    if matches_int.get('limit'): AlfaChannel.finds['controls']['cnt_tot'] = matches_int.get('limit', findS['controls']['cnt_tot'])
    
    matches_int = matches_int.get("_embedded", {}).get("items", {})
    if not matches_int: return matches
    
    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)
        
        try:
            elem_json['url'] = "%sembed/%s" % (host, elem.get('uuid', 0))
            elem_json['title'] = elem.get('title', '')
            elem_json['thumbnail'] = elem.get('thumbnailsList', [])[0] if elem.get('thumbnailsList', []) else ''
            elem_json['stime'] = elem.get('durationInSeconds', 0)
            elem_json['quality'] = 'HD' if elem.get('isHD') else ''
        
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
    
    item.url = "%sapi/search/list?order=%s&orientation=%s&q=%s&p=1&ssr=false" % (host, "date", item.orientation, texto.replace(" ", "+"))
    
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
