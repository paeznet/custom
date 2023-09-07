# -*- coding: utf-8 -*-
# -*- Channel PorntubeNL -*-
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
             'channel': 'porntubenl', 
             'host': config.get_setting("current_host", 'porntubenl', default=''), 
             'host_alt': ["https://www.google.com/"], 
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

finds = {'find': dict([('find', [{'tag': ['div', 'main'], 'id': ['primary', 'main']}]),
                       ('find_all', [{'tag': ['article'], 'class': [re.compile(r"^post-\d+"), 'thumb-block']}])]), 
                 # {'find_all': [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}]},
         'categories':dict([('find', [{'tag': ['div'], 'class': ['videos-list']}]),
                            ('find_all', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}])]), 
                       # {'find_all': [{'tag': ['article'], 'class': [re.compile(r"^post-\d+")]}]},
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         # 'next_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]),
                            # ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]), 
         # 'next_page': dict([('find', [{'tag': ['div'], 'class': ['pagination-page-bas']}, {'tag': ['span']}]),
                            # ('find_next_sibling', [{'tag': ['a'], '@ARG': 'href'}])]), 
         # 'next_page': dict([('find', [{'tag': ['a'], 'class': 'tm_pag_nav_next', '@ARG': 'href'}])]), 
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': dict([('find', [{'tag': ['div', 'nav'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': 'page/(\d+)'}])]), 
         # 'last_page':  dict([('find', [{'tag': ['script'], 'string': re.compile('(?i)var objectPagination')}]), 
                             # ('get_text', [{'tag': '', 'strip': True, '@TEXT': 'total:\s*(\d+)'}])]), 
         # 'last_page': {},
         'plot': {}, 
         ####   fuckingsession
         #'findvideos': dict([('find', [{'tag': ['div'], 'itemprop': ['articleBody']}]), 
         #                    ('find_all', [{'tag': ['a', 'iframe'], '@ARG': ['href', 'src']}])]),
         # 'findvideos': dict([('find', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}]), 
                             # ('find_all', [{'tagOR': ['a'], 'href': True, 'rel': 'noopener'},
                                           # {'tag': ['iframe'], 'src': True}])]),
         'findvideos': dict([('find', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}]), 
                             ('find_all', [{'tagOR': ['a'], 'href': True, 'id': 'tracking-url'},
                                           {'tag': ['iframe'], 'src': True}])]),


         # 'findvideos': {'find': [{'tag': ['div'], 'class': ['responsive-player']}, {'tag': ['iframe'], '@ARG': 'src'}]},
                       # dict([('find', [{'tag': ['li'], 'class': 'link-tabs-container', '@ARG': 'href'}]),
                             # ('find_all', [{'tag': ['a'], '@ARG': 'href'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            # 'list_all_title': dict([('find', [{'tag': ['h2']}]),
                                                    # ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'list_all_thumbnail': {'find': [{'tag': ['video'], '@ARG': ['poster']}]},

                            # 'list_all_stime': dict([('find', [{'tag': ['span'], 'class': ['duration']}]),
                                                    # ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'list_all_quality': dict([('find', [{'tag': ['span'], 'class': ['hd-video']}]),
                                                      # ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'section_cantidad': dict([('find', [{'tag': ['span'], 'class': ['vids']}]),
                                                      # ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(\d+)'}])])
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
    
    logger.error(AlfaChannel.domains_updated) 
    
    return itemlist

