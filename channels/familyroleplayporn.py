# -*- coding: utf-8 -*-
# -*- Channel FamilyRolePlayPorn -*-
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

# https://latestpornvideo.com/   https://hdporn92.com/
# https://mynewpornvideo.com/   https://newpornvideo.xyz/
# https://trashxxx.com/     https://whereismyporn.com/
# https://familyroleplayporn.com/
# https://vidzxxxhd.com/

################     OUT 12-2023


canonical = {
             'channel': 'familyroleplayporn', 
             'host': config.get_setting("current_host", 'familyroleplayporn', default=''), 
             'host_alt': ["https://familyroleplayporn.com/"], 
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
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': dict([('find', [{'tag': ['div', 'nav'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': 'page/(\d+)'}])]), 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}]), 
                             ('find_all', [{'tagOR': ['a'], 'href': True, 'id': 'tracking-url'},
                                           {'tag': ['iframe'], 'src': True}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            # 'list_all_title': dict([('find', [{'tag': ['h2']}]),
                                                    # ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'list_all_stime': dict([('find', [{'tag': ['span'], 'itemprop': ['duration']}]),
                                                    # ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'list_all_quality': dict([('find', [{'tag': ['span'], 'class': ['hd-video']}]),
                                                      # ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'section_cantidad': dict([('find', [{'tag': ['span'], 'class': ['vids']}]),
                                                      # ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(\d+)'}])])
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
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "page/1/?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:categories|channels|models|pornstars|actor)\/[^$]+$)', r'\1?filter=latest"']]
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    findS['controls']['action'] = 'findvideos'
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


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
