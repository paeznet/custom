# -*- coding: utf-8 -*-
# -*- Channel blackporn -*-
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

#  https://txxx.com  https://hclips.com    https://hdzog.com  https://hotmovs.com   
#  https://tubepornclassic.com  https://upornia.com    https://vjav.com   https://voyeurhit.com  
#  https://desiporn.tube/   https://manysex.com/  https://porntop.com/   https://shemalez.com/  https://thegay.com/ 
#  https://pornzog.com/   https://tporn.xxx/  https://see.xxx/   https://blackporn.tube/  
#  https://mrgay.com/  https://gettranny.com/  

canonical = {
             'channel': 'blackporn', 
             'host': config.get_setting("current_host", 'blackporn', default=''), 
             'host_alt': ["https://blackporn.tube/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
url_api = host + "api/json/videos2/%s/%s/%s/30/%s.%s.1.all..%s.json"
                # api/json/videos2/86400/str/latest-updates/30/..1.all...json
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
         'next_page_rgx': [['\.\d+.all\.', '.%s.all.'], ['\/\d+\.json', '/%s.json'], ['\.\d+\.json', '.%s.json']], 
         'last_page': {}, 
         'plot': {}, 
         'findvideos': {}, 
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''], ['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'controls': {'url_base64': False, 'cnt_tot': 30, 'reverse': False}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)

def mainlist(item):
    logger.info()
    itemlist = []
    soup = AlfaChannel.create_soup(host, alfa_s=True) #Para coger canonical
    
    itemlist.append(Item(channel=item.channel, title="Ultimas" , action="list_all", url=url_api % ("86400", "str", "latest-updates", "", "", "")))
    itemlist.append(Item(channel=item.channel, title="Mejor valoradas" , action="list_all", url=url_api % ("86400", "str", "top-rated", "", "", "month")))
    itemlist.append(Item(channel=item.channel, title="Mas popular" , action="list_all", url=url_api % ("86400", "str", "most-popular", "", "", "month")))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="list_all",  url=url_api % ("86400", "str", "most-commented", "", "", "month") ))
    itemlist.append(Item(channel=item.channel, title="Mas Largo" , action="list_all", url=url_api %  ("86400", "str", "longest", "", "", "")))
    itemlist.append(Item(channel=item.channel, title="Pornstar" , action="section", url=host + "api/json/models/86400/%s/filt..ebony......../most-popular/30/1.json" %"str", extra="PornStars"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "api/json/channels/86400/%s/most-viewed/30/..1.json" %"str", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "api/json/categories/14400/%s.all.json" %"str", extra="Categorías"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", orientation="str"))
    
    # itemlist.append(Item(channel = item.channel, title = ""))
    
    # itemlist.append(Item(channel=item.channel, title="Trans", action="submenu", orientation="she"))
    # itemlist.append(Item(channel=item.channel, title="Gay", action="submenu", orientation="gay"))
    
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Ultimas" , action="list_all", url=url_api % ("14400", item.orientation, "latest-updates", "", "", "")))
    itemlist.append(Item(channel=item.channel, title="Mejor valoradas" , action="list_all", url=url_api % ("14400", item.orientation, "top-rated", "", "", "month")))
    itemlist.append(Item(channel=item.channel, title="Mas popular" , action="list_all", url=url_api % ("14400", item.orientation, "most-popular", "", "", "month")))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="list_all",  url=url_api % ("14400", item.orientation, "most-commented", "", "", "month") ))
    itemlist.append(Item(channel=item.channel, title="Mas Largo" , action="list_all", url=url_api %  ("14400", item.orientation, "longest", "", "", "")))
    itemlist.append(Item(channel=item.channel, title="Pornstar" , action="section", url=host + "api/json/models/86400/%s/filt........../most-popular/60/1.json" %item.orientation, orientation=item.orientation, extra="PornStars"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "api/json/channels/14400/%s/most-viewed/80/..1.json" %item.orientation, orientation=item.orientation, extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "api/json/categories/14400/%s.all.json" %item.orientation, orientation=item.orientation, extra="Categorías"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", orientation=item.orientation))
    return itemlist


def section(item):
    logger.info()
    
    return AlfaChannel.section(item, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    if not item.orientation:
        item.orientation = "str"
    
    if matches_int.get('total_count'):
        total = matches_int.get('total_count', 0)
        AlfaChannel.last_page = int((float(total) / float(finds['controls'].get('cnt_tot', 20))) + 0.999999)
    
    if "Categorías" in item.extra: 
        matches_int = matches_int.get('categories', {}).copy()
        c_type = 'categories'
    if "Canal" in item.extra: 
        matches_int = matches_int.get('channels', {}).copy()
        c_type = 'channel'
    if "PornStars" in item.extra: 
        matches_int = matches_int.get('models', {}).copy()
        c_type = 'model'
    
    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)
        try:
            elem_json['url'] = url_api % ("86400", item.orientation, "latest-updates", c_type ,  elem.get('dir', ''), "")
            elem_json['title'] = elem.get('title', '')
            elem_json['thumbnail'] = elem.get('img', '') if  elem.get('img', '') else '' \
                                     or elem.get('scr1', '') if  elem.get('scr1', '') else ''
            if  elem.get('cf3', ''):  elem_json['thumbnail'] = elem.get('cf3', '')
            if  elem.get('total_videos', ''):  elem_json['cantidad'] = elem.get('total_videos', '')
            else: elem_json['cantidad'] =  elem.get('statistics', {}).get('videos', '')
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
    
    if matches_int.get('total_count'):
        total = matches_int.get('total_count', 0)
        AlfaChannel.last_page = int((float(total) / float(finds['controls'].get('cnt_tot', 20))) + 0.999999)
    
    matches_int = matches_int['videos'].copy()
    
    for elem in matches_int:
        elem_json = {}
       
        try:
            elem_json['url'] = "%svideos/%s/%s/" % (host, elem.get('video_id', 0), elem.get('dir', ''))
            elem_json['title'] = elem.get('title', '')
            elem_json['thumbnail'] = elem.get('scr', '') if elem.get('scr', '') else ''
            elem_json['stime'] = elem.get('duration', 0)
            quality = elem.get('file_dimensions', '').split('x') if elem.get('file_dimensions') else ''
            elem_json['quality'] = "%sp" % quality[-1]
            elem_json['star'] = elem.get('models', '') if elem.get('models', '') else ''
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
    
    item.url = "%sapi/videos.php?params=259200/%s/latest-updates/60/search..1.all..&s=%s&sort=latest-updates&date=all&type=all&duration=all" % (host,item.orientation, texto.replace(" ", "%20")) 
    
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
