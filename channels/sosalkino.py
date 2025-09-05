# -*- coding: utf-8 -*-
# -*- Channel sosalkino -*-
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

# forced_proxy_opt = 'ProxySSL'
forced_proxy_opt = ''


canonical = {
             'channel': 'sosalkino', 
             'host': config.get_setting("current_host", 'sosalkino', default=''), 
             'host_alt': ["https://wvw.sosalkino.guru/"], 
             'host_black_list': ["https://wvw.sosalkino.tube/"], 
             'set_tls': None, 'set_tls_min': False, 'retries_cloudflare': 5, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'cf_assistant': False, 'CF_stat': True, 
             'CF': False, 'CF_test': False, 'alfa_s': True
             # 'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             # 'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 35
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []

finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['video_list']}]),
                       ('find_all', [{'tag': ['div'], 'class': ['item']}])]),     #'id': re.compile(r"^browse_\d+")}]},
         'categories': dict([('find', [{'tag': ['div'], 'class': ['items-list']}]),
                             ('find_all', [{'tag': ['div'], 'class': ['item']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['div', 'ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]),
         'next_page_rgx': [['\/\d+', '/%s'], ['&from_videos=\d+', '&from_videos=%s']], 
         'last_page': {},
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                           },
         'controls': {'url_base64': False, 'cnt_tot': 24, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host))
    itemlist.append(Item(channel=item.channel, title="Mas Vistos" , action="list_all", url=host + "most-popular/month/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=host + "top-rated/month/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "studios/", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "actresses/", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "porno-categ/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    # findS['url_replace'] = [['(\/(?:categories|channels|models|pornstars)\/[^$]+$)', r'\1?sort_by=post_date&from=1']]
    
    if item.extra == 'PornStar':
        findS['controls']['cnt_tot'] = 20
    
    if item.extra == 'Categorias':
        findS['categories'] = dict([('find', [{'tag': ['div'], 'class': ['active']}]), 
                                    ('find_all', [{'tag': ['div'], 'class': ['item']}])])
    # return AlfaChannel.section(item, finds=findS, **kwargs)
    return AlfaChannel.section(item, finds=findS, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        
        elem_json = {}
        
        try:
            if elem.find('span', class_='letter'): continue
            elem_json['url'] = elem.get("href", '') or elem.a.get("href", '')
            elem_json['title'] = elem.find(class_=['title']).get_text(strip=True)
            if elem.img: elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                                                                     or elem.img.get('data-src', '') \
                                                                                     or elem.img.get('src', '')
            elem_json['cantidad'] = elem.find('span', class_=['quantity']).get_text(strip=True)
            if "categories" in elem_json['url']:
                elem_json['title'] = scrapertools.find_single_match(elem_json['url'], 'categories/([A-z0-9-]+)').replace("-", " ")
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        if not elem_json['url']: continue
        matches.append(elem_json.copy())
    return matches


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    
    if item.extra == 'Search':
        findS['controls']['cnt_tot'] = 12
        findS['next_page'] = {}
        item.last_page = 9999
    
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
            elem_json['title'] = scrapertools.find_single_match(elem_json['url'], 'videos/([A-z0-9-]+)').replace("-", " ")
            elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') \
                                     or elem.img.get('src', '')
            elem_json['stime'] = elem.find('span',class_='text').get_text(strip=True) if elem.find('span', class_='text') else ''
            if elem.find('div', class_='premium-icons').find('img') \
                and "diamond" in elem.find('div', class_='premium-icons').img['src']:
                elem_json['premium'] = "Premium"
        
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


def play(item):
    logger.info()
    itemlist = []
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    if soup.find('div', class_='models-list'):
        pornstars = soup.find('div', class_='models-list').find_all('a', class_='link') #, href=re.compile("/models/[A-z0-9-]+(?:/|)")
        for x, value in enumerate(pornstars):
            pornstars[x] = value.p.get_text(strip=True)
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s' %pornstar
        if AlfaChannel.color_setting.get('quality', '') in item.contentTitle:
            lista.insert (2, pornstar)
        else:
            lista.insert (1, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.extra = 'Search'
    
    item.url = "%ssearch/?q=%s&from_videos=1" % (host, texto.replace(" ", "+"))
    # item.url = "%ssearch/video/?s=%s&o=recent&page=1" % (host, texto.replace(" ", "+"))
    
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
