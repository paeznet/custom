# -*- coding: utf-8 -*-
# -*- Channel xxvideoss -*-
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
             'channel': 'xxvideoss', 
             'host': config.get_setting("current_host", 'xxvideoss', default=''), 
             'host_alt': ["https://xxvideoss.org/"], 
             'host_black_list': [], 
             # 'set_tls': None, 'set_tls_min': False, 'retries_cloudflare': 5, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             # 'cf_assistant': False, 'CF_stat': True, 
             # 'CF': False, 'CF_test': False, 'alfa_s': True
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

finds = {'find': dict([('find', [{'tag': ['main'], 'id': ['main']}]),
                       ('find_all', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}])]),
         'categories': dict([('find', [{'tag': ['main'], 'id': ['main']}]),
                             # ('find_all', [{'tag': ['div'], 'style': ['300px\\;']}])]),
                             ('find_all', [{'tag': ['a']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+\/', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['nav'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'href', '@TEXT': 'page/(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['iframe'], '@ARG': 'src'}]},
                       # dict([('find', [{'tag': ['header'], 'class': ['entry-header']}]), 
                             # ('find_all', [{'tagOR': ['a'], 'href': True, 'id': 'tracking-url'},
                                           # {'tag': ['meta'], 'content': True, 'itemprop': 'embedURL'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                           },
         'controls': {'url_base64': False, 'cnt_tot': 20, 'reverse': False, 'profile': 'default'}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel = item.channel, title="Nuevos" , action="list_all", url=host + "page1/?filter=latest"))
    # itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "top-porn-stars-watch-full-videos-of-the-hottest-adult-actresses-online/", extra="PornStar"))
    itemlist.append(Item(channel = item.channel, title="Canal" , action="section", url=host + "legal-notice/", extra="Canal"))
    itemlist.append(Item(channel = item.channel, title="Categorias" , action="section", url=host + "most-popular-adult-video-categories/", extra="Categorias"))
    itemlist.append(Item(channel = item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    # if "PornStar" in item.extra:
        # findS['categories'] = dict([('find', [{'tag': ['article']}]),
                                    # ('find_all', [{'tag': ['a']}])]),
    if "Canal" in item.extra:
        findS['categories'] = dict([('find', [{'tag': ['aside'], 'id': ['block-23']}]),
                                    ('find_all', [{'tag': ['a']}])])
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    findS['controls']['action'] = 'findvideos'
    
    # return AlfaChannel.list_all(item, finds=findS, **kwargs)
    return AlfaChannel.list_all(item, finds=findS, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    soup = AHkwargs.get('soup', {})
    
    for elem in matches_int:
        
        elem_json = {}
        
        try:
            
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.a.get('title', '') \
                                 or elem.find(class_='title').get_text(strip=True) if elem.find(class_='title') else ''
            if not elem_json['title']:
                elem_json['title'] = elem.img.get('alt', '')
            
            thumbnail = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                        or elem.img.get('data-src', '') \
                        or elem.img.get('src', '')
            elem_json['thumbnail'] = thumbnail.replace("–", "%E2%80%93")
            elem_json['stime'] = elem.find(class_='duration').get_text(strip=True) if elem.find(class_='duration') else ''
            
            # elem_json['premium'] = elem.find('i', class_='premiumIcon') \
                                     # or elem.find('span', class_=['ico-private', 'premium-video-icon']) or ''
            
            # if elem.find('div', class_='videoDetailsBlock') \
                                     # and elem.find('div', class_='videoDetailsBlock').find('span', class_='views'):
                # elem_json['views'] = elem.find('div', class_='videoDetailsBlock')\
                                    # .find('span', class_='views').get_text('|', strip=True).split('|')[0]
            # elif elem.find('span', class_='video_count'):
                # elem_json['views'] = elem.find('span', class_='video_count').get_text(strip=True)
        
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
    
    soup = AHkwargs.get('soup', {})
    
    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            if isinstance(elem, str):
                elem_json['url'] = elem
                if elem_json['url'].endswith('.jpg'): continue
            else:
                elem_json['url'] = elem.get("href", "") or elem.get("src", "")
            elem_json['language'] = ''
            
            
            pornstars = soup.find('span', class_='tag-links').find_all('a', href=re.compile(r"/(?:tag|pornstar|actor)/[A-z0-9-]+/"))
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
