# -*- coding: utf-8 -*-
# -*- Channel WatchErotic -*-
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
forced_proxy_opt = 'ProxySSL'


######      KTP   ---->     https://bbaze.top/eu46/default.mp4
######      Fallan fotos https://watcherotic.com/contents/videos_screenshots/3000/3444/336x189/4.jpg hasta con |verifypeer=false
#                        https://watcherotic.com/contents/videos_screenshots/3000/3444/320x180/4.jpg
canonical = {
             'channel': 'watcherotic', 
             'host': config.get_setting("current_host", 'watcherotic', default=''), 
             'host_alt': ["https://watcherotic.com/"], 
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

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['item', 'preview']}]},
         'categories': {'find_all': [{'tag': ['div'], 'class': ['thumb']}]},
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['&from_videos=\d+', '&from_videos=%s'], ['&from=\d+', '&from=%s'], 
                           ['/\d+', '/%s/'], ['&page=\d+', '&page=%s'], ['\?page=\d+', '?page=%s'], ['\/page\/\d+\/', '/page/%s/']], 
         'last_page':dict([('find', [{'tag': ['div'], 'class': ['pagination']}]),
                           ('find_all', [{'tag': ['a'], '@POS': [-2], '@ARG': 'data-parameters', '@TEXT': ':(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'section_cantidad': dict([('find', [{'tag': ['div'], 'class': ['thumb-item']}]),
                                                      ('get_text', [{'strip': True}])])
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
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=host + "search/?sort_by=post_date&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="list_all", url=host + "search/?sort_by=video_viewed_month&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor Valorada" , action="list_all", url=host + "search/?sort_by=rating_month&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Favoritas" , action="list_all", url=host + "search/?sort_by=most_favourited&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Comentadas" , action="list_all", url=host + "search/?sort_by=most_commented&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Largas" , action="list_all", url=host + "search/?sort_by=duration&from_videos=1"))
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "channels/?sort_by=total_videos&from=1", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "models/?sort_by=total_videos&from=1", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "tags/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:tags|models)\/[^$]+$)', r'\1?sort_by=post_date&from=1']]
    
    if "Categorias" in item.extra:
        findS['categories'] = dict([('find', [{'tag': ['ul'], 'class': ['tags-list']}]),
                                    ('find_all', [{'tag': ['a']}])])
        findS['profile_labels']['section_title']= dict([('find', [{'tag': ['span']}]),
                                                           ('get_text', [{'strip': True}])])
        findS['profile_labels']['section_cantidad']= dict([('find', [{'tag': ['em']}]),
                                                           ('get_text', [{'strip': True}])])
    if item.extra == 'PornStar':
        item.last_page = 9999
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    if "Categorias" in item.extra:
        findS['controls']['cnt_tot']=30
    if item.extra == 'PornStar':
        findS['controls']['cnt_tot']=12
    
    # return AlfaChannel.list_all(item, **kwargs)
    return AlfaChannel.list_all(item, finds=findS, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.a.get('title', '')
            elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') \
                                     or elem.img.get('src', '')
            
            elem_json['thumbnail'] = elem_json['thumbnail'].replace("336x189", "320x180")
            
            elem_json['stime'] = elem.find(class_='time').get_text(strip=True) if elem.find(class_='time') else ''
            if elem.find('div', class_=['qualtiy']):
                elem_json['quality'] = 'HD'
            elem_json['premium'] = elem.find('i', class_='premiumIcon') \
                                     or elem.find('span', class_=['ico-private', 'premium-video-icon']) or ''
            if elem.find('span', class_='views'):
                elem_json['views'] = elem.find('span', class_='views').get_text(strip=True)
            
            
            
            
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
    
    item.url = "%ssearch/video/?s=%s&o=recent&page=1" % (host, texto.replace(" ", "+"))
    
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
