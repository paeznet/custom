# -*- coding: utf-8 -*-
# -*- Channel ViralxPorno -*-
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
             'channel': 'viralxporno', 
             'host': config.get_setting("current_host", 'viralxporno', default=''), 
             'host_alt': ["https://viralxporno.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 10
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []

finds = {'find': dict([('find', [{'tag': ['article']}]), 
                        ('find_all', [{'tag': ['section'], 'class': ['pst-cn']}])]),
         'categories':  dict([('find', [{'tag': ['nav'], 'class': ['ctr']}]), 
                              ('find_all', [{'tag': ['li'], 'id': re.compile(r"menu-item-\d+")}]) ]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['wp-pagenavi']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href', '@TEXT': 'page/(\d+)'}])]), 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['div'], 'class': ['video-carousel']}]),
                             ('find_all', [{'tag': ['iframe']}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', ''], ['Imagen ', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
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
    
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=host + "page/1"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host, extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/[^$]+$)', r'\1page/1']]
    if item.extra == 'Canal':
        findS['last_page'] = {}
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    findS['controls']['action'] = 'findvideos'
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


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
            url = elem.get("data-lazy-src", "") or elem.get("src", "")
            if "?post_id=" in url:
                data = AlfaChannel.create_soup(url, **kwargs)
                url = data.iframe.get('src', '')
                
            if "player-x.php?" in url:
                data = AlfaChannel.convert_url_base64(url, host)  	####  DECODE
                data =AlfaChannel.do_unquote(data)			####  quita %20  urlparse.unquote(url)
                data = AlfaChannel.do_soup(data)			####  BeautifulSoup(url, "html5lib", from_encoding="utf-8")
                url = data.source['src']
                url += "|Referer=%s" % host
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
