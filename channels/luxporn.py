# -*- coding: utf-8 -*-
# -*- Channel luxporn -*-
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

forced_proxy_opt = ''  #'ProxySSL'


canonical = {
             'channel': 'luxporn', 
             'host': config.get_setting("current_host", 'luxporn', default=''), 
             'host_alt': ["https://luxporn.cc/"], 
             'host_black_list': [], 
             # 'set_tls': None, 'set_tls_min': False, 'retries_cloudflare': 5, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             # 'cf_assistant': False, 'CF_stat': True, 
             # 'CF': False, 'CF_test': False, 'alfa_s': True
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 40
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []


finds = {'find':  dict([('find', [{'tag': ['div'], 'id': ['archive-content', 'contenedor']}]),
                             ('find_all', [{'tag': ['article'], 'id': re.compile(r"^post-\d+")}])]),
                             # {'find_all': [{'tag': ['article'], 'id': re.compile(r"^post-\d+")}]},
         'categories': dict([('find', [{'tag': ['ul'], 'class': ['genres']}]),
                             ('find_all', [{'tag': ['li']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]),
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]), 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': {},
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['div'], 'class': ['content']}]), 
                             ('find_all', [{'tagOR': ['li'], 'id': re.compile(r"^player-option-\d+")},
                                           {'tag': ['iframe'], 'src': True}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', ''],['Placeholder:\s*','']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                           },
         'controls': {'url_base64': False, 'cnt_tot': 25, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Peliculas" , action="list_all", url=host + "movies/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Mejor Valoradas" , action="list_all", url=host + "ratings/page/1/?get=movies"))
    itemlist.append(Item(channel=item.channel, title="Tendencia" , action="list_all", url=host + "trending/page/1/?get=movies"))
    
    itemlist.append(Item(channel=item.channel, title="Videos" , action="list_all", url=host + "tvshows/page/1/"))
    
    itemlist.append(Item(channel=item.channel, title="Año" , action="section", url=host, extra="Abc"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host, extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:category|actress)\/[^$]+$)', r'\1page/1/']]
    
    if item.extra == 'Abc':
        findS['categories'] =  dict([('find', [{'tag': ['ul'], 'class': ['releases']}]),
                                     ('find_all', [{'tag': ['li']}]) ])
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    findS['controls']['action'] = 'findvideos'
    
    if item.extra == "Search":
        findS['find'] =  dict([('find', [{'tag': ['div'], 'class': ['search-page']}]),
                               ('find_all', [{'tag': ['article']}])])
        
        # findS['next_page']= dict([('find', [{'tag': ['a'], 'class': ['g1-load-more'],
                                   # '@ARG': 'data-g1-next-page-url'}])]) 
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
            thumbnail = elem.img.get('data-thumb_url', '') \
                        or elem.img.get('data-original', '') \
                        or elem.img.get('data-src', '') \
                        or elem.img.get('src', '')
            elem_json['thumbnail'] = re.sub(r"-185x278", "", thumbnail)
            elem_json['title']  = elem.img.get('alt', '') \
                                  or elem.h4.get_text(strip=True)
        
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
            if elem.get('src', ''):
                elem_json['url'] = elem.get('src', '')
            else:
                ttt = elem['data-post']
                nume =  elem['data-nume']
                type = elem['data-type']
                post = {'action': 'doo_player_ajax', 'post': ttt, 'nume': nume, 'type': type}
                post_url= "%swp-admin/admin-ajax.php" %host
                data = AlfaChannel.httptools.downloadpage(post_url, post=post, **kwargs).json
                elem_json['url'] = data['embed_url']
            
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
    
    item.extra = "Search"
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
