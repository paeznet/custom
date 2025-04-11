# -*- coding: utf-8 -*-
# -*- Channel MyDadsPies -*-
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
             'channel': 'mydadspies', 
             'host': config.get_setting("current_host", 'mydadspies', default=''), 
             'host_alt': ["https://mydadspies.com/"], 
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

finds = {'find':  {'find_all': [{'tag': ['div'], 'class': ['video-block']}]},
         'categories': dict([('find', [{'tag': ['div'], 'id': ['primary']}]),
                             ('find_all', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}])]), 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['div', 'ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]),
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': {},
         'plot': {}, 
         'findvideos': {},
         'findvideos': dict([('find', [{'tag': ['section'], 'class': ['single-video-player']}]), 
                             ('find_all', [{'tagOR': ['a'], 'href': True, 'rel': 'noopener'},
                                           {'tag': ['meta'], 'content': True, 'itemprop': 'embedURL'}])]),
                                           
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'list_all_quality': dict([('find', [{'tag': ['span'], 'class': ['hd-video']}]),
                                                      ('get_text', [{'tag': '', 'strip': True}])]),
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
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "page/1/?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="list_all", url=host + "page/1/?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=host + "page/1/?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=host + "page/1/?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "ebony-porn-actresses/page/1/", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "channels/page/1/", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "categories/page/1/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:categories|channels|models|pornstars|actor)\/[^$]+$)', r'\1?filter=latest']]
    if item.extra == 'Canal':
        findS['categories'] = {'find_all': [{'tag': ['div'], 'class': ['sow-image-grid-image']}]}
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
    
    soup = AHkwargs.get('soup', {})
    
    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)
        
        try:
            if isinstance(elem, str):
                elem_json['url'] = elem
                if elem_json['url'].endswith('.jpg'): continue
            else:
                elem_json['url'] = elem.get("href", "") or elem.get("content", "")
            elem_json['language'] = ''
            
            if "php?q=" in elem_json['url']:
                import base64
                url = elem_json['url'].split('php?q=')
                url_decode = base64.b64decode(url[-1]).decode("utf8")
                url = AlfaChannel.do_unquote(url_decode)
                elem_json['url'] = scrapertools.find_single_match(url, '<(?:iframe|source) src="([^"]+)"')
                
            
            pornstars = soup.find_all('a', href=re.compile(r"/(?:cast|pornstar|actor)/[A-z0-9-]+"))
            if pornstars:
                for x, value in enumerate(pornstars):
                    pornstars[x] = value.get_text(strip=True)
                pornstar = '& '.join(pornstars)
                # pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
                elem_json['plot'] = pornstar
            
            
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())

        if not elem_json.get('url', ''): continue

        matches.append(elem_json.copy())

    return matches, langs

def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    # item.url = "%sbuscar/?q=%s&sort_by=video_viewed&from_videos=1" % (host, texto.replace(" ", "+"))
    item.url = "%s?s=%s&filter=latest" % (host, texto.replace(" ", "+"))
    
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
