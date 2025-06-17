# -*- coding: utf-8 -*-
# -*- Channel BigBoobsxxx -*-
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


# https://bigboobsxxx.com/new/?sort_by=post_date_and_popularity&mode=&function=get_block&block_id=list_videos_all_thumb&from=1
# https://bigboobsxxx.com/new/?from=1

# https://bigboobsxxx.com/best/?sort_by=video_viewed&function=get_block&block_id=list_videos_all_thumb&from=1
# https://bigboobsxxx.com/best/?sort_by=ctr&function=get_block&block_id=list_videos_all_thumb&from=1

# https://bigboobsxxx.com/models/?sort_by=max_videos_ctr&from=2&mode=async&function=get_block&block_id=list_models_models_list
# https://bigboobsxxx.com/categories/?sort_by=max_videos_ctr&mode=&function=get_block&block_id=list_categories_categories_list&from=1
# https://bigboobsxxx.com/huge-tits/findS['url_replace'] = [['([^$]+$)', r'\1&filter=latest&paged=1']] >>>>> https://baddiehub.com/?cat=90 + &filter=latest
# https://bigboobsxxx.com/search/big-tits/?sort_by=video_viewed&mode=&function=get_block&block_id=list_videos_thumb&from=2|Referer=https://bigboobsxxx.com/
# https://bigboobsxxx.com/search/big-tits/?sort_by=post_date_and_popularity&mode=async&function=get_block&block_id=list_videos_thumb&from=2


canonical = {
             'channel': 'bigboobsxxx', 
             'host': config.get_setting("current_host", 'bigboobsxxx', default=''), 
             'host_alt': ["https://bigboobsxxx.com/"], 
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

finds = {'find': {'find_all': [{'tag': ['section'], 'class': ['item']}]}, ##'id': re.compile(r"^vf\d+")
         'categories': {'find_all': [{'tag': ['section'], 'class': ['item']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         # 'next_page': dict([('find', [{'tag': ['div'], 'class': ['load-more']}]), 
                            # ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]), 
         'next_page_rgx': [['\?from=\d+', '?from=%s']], 
         'last_page': {}, 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['load-more']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'data-parameters', '@TEXT': '\:(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {}, 
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'controls': {'url_base64': False, 'cnt_tot': 30, 'reverse': False, 'profile': 'default'}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)

def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Nuevos", action="list_all", url=host + "new/?from=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado", action="list_all", url=host + "best/?from=1"))
    itemlist.append(Item(channel=item.channel, title="Pornstars", action="section", url=host + "models/?from=1", extra="Pornstar"))
    itemlist.append(Item(channel=item.channel, title="Categorias", action="section", url=host + "categories/?from=1", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['($)', r'\1new/?from=1']]
    
    if item.extra == 'Categorias':
        findS['controls']['cnt_tot'] = 9999
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    item.last_page = 9999
    # return AlfaChannel.list_all(item, **kwargs)
    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()
    
    matches = []
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            # if elem.find('div', class_='thumbTextPlaceholder'): continue
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.a.get('title', '') or elem.h2.get_text(strip=True)
            elem_json['thumbnail'] = elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') \
                                     or elem.img.get('src', '')
            elem_json['stime'] = elem.find('span', class_='dr').get_text(strip=True) if elem.find('span', class_='dr') else ''
            elem_json['quality'] = elem.find('span', class_='qt').get_text(strip=True) if elem.find('span', class_='qt') else ''
            
            # if elem.find('span', class_='mbvie'):
                # elem_json['views'] = elem.find('span', class_='mbvie').get_text(strip=True)
            pornstars = elem.find_all('span', itemprop="actor")
            if pornstars:
                for x, value in enumerate(pornstars):
                    pornstars[x] = value.get_text(strip=True)
                elem_json['star'] = ' & '.join(pornstars)
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        # if elem_json['premium']: continue
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
    if soup.find_all('li', class_="starw"):
        pornstars = soup.find_all('li', class_="starw")
        
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s' %pornstar
        lista.insert (2, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/%s/?from=1&sort_by=post_date_and_popularity&mode=async&function=get_block&block_id=list_videos_thumb" % (host, texto.replace(" ", "-"))
    
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
