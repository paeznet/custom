# -*- coding: utf-8 -*-
# -*- Channel 12milf -*-
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
             'channel': 'pornobae', 
             'host': config.get_setting("current_host", 'pornobae', default=''), 
             'host_alt': ["https://pornobae.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
             # 'set_tls': None, 'set_tls_min': False, 'retries_cloudflare': 5, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             # 'cf_assistant': False, 'CF_stat': True, 
             # 'CF': True, 'CF_test': False, 'alfa_s': True
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
         'categories': {'find_all': [{'tag': ['article'], 'id': re.compile(r"^post-\d+")}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+\/', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': 'page/(\d+)'}])]), 
         'plot': {}, 
         #'findvideos': dict([('find', [{'tag': ['div'], 'itemprop': ['articleBody']}]), 
         #                    ('find_all', [{'tag': ['a', 'iframe'], '@ARG': ['href', 'src']}])]),
         'findvideos': dict([('find', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}]), 
                             ('find_all', [{'tagOR': ['a'], 'href': True, 'class': ['descarga']},
                                           {'tag': ['iframe'], 'src': True}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'controls': {'url_base64': False, 'cnt_tot': 24, 'reverse': False, 'profile': 'default'}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel = item.channel, title="Nuevos" , action="list_all", url=host + "page/1/?filter=latest"))
    itemlist.append(Item(channel = item.channel, title="Mas vistos" , action="list_all", url=host + "page/1/?filter=most-viewed"))
    itemlist.append(Item(channel = item.channel, title="Mejor valorado" , action="list_all", url=host + "page/1/?filter=popular"))
    itemlist.append(Item(channel = item.channel, title="Mas metraje" , action="list_all", url=host + "page/1/?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "actors/page/1/", extra="PornStar"))
    itemlist.append(Item(channel = item.channel, title="Canal" , action="section", url=host + "categories/page/1/", extra="Canal"))
    itemlist.append(Item(channel = item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:category|actor)\/[^$]+$)', r'\1page/1/?filter=latest']]
    # if "Categorias" in item.extra:
        # findS['controls']['cnt_tot'] = 9999
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    findS['controls']['action'] = 'findvideos'
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)
    # return AlfaChannel.list_all(item, **kwargs)


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
    srv_ids = {"dood": "Doodstream",
               "Streamtape": "Streamtape ",
               "sbthe": "Streamsb",
               "tubexplayer": "Tiwikiwi",
               "VOE": "voe",
               "mixdrop.co": "Mixdrop",
               "Upstream": "Upstream"}
    
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    
    if soup.find('div', id='video-actors'):
        pornstars = soup.find('div', id='video-actors').find_all('a', href=re.compile("/actor/[A-z0-9-]+/"))
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        item.plot = pornstar
        # lista = item.contentTitle.split()
        # if AlfaChannel.color_setting.get('quality', '') in item.contentTitle:
            # lista.insert (4, pornstar)
        # else:
            # lista.insert (2, pornstar)
        # item.contentTitle = ' '.join(lista)
    
    
    for elem in matches_int:
        elem_json = {}
        # logger.error(elem)
        
        try:
            if isinstance(elem, str):
                elem_json['url'] = elem
                if elem_json['url'].endswith('.jpg'): continue
            else:
                elem_json['url'] = elem.get("href", "") or elem.get("src", "")
            if AlfaChannel.obtain_domain(elem_json['url']):
                elem_json['server'] = AlfaChannel.obtain_domain(elem_json['url']).split('.')[-2]
            else: 
                elem_json['server'] = "dutrag"  ### Quitar los watch/YnqAKRJybm2PJ  aparecen en movies
            if elem_json['server'] in ["Netu", "trailer", "k2s", "dutrag", "adtng"]: continue
            elem_json['server'] = ''
            # if elem_json['server'] in srv_ids:
                # elem_json['server'] = srv_ids[elem_json['server']]
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
    
    item.url = "%spage/1/?s=%s&filter=latest" % (host, texto.replace(" ", "+"))
    
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
