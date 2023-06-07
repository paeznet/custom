# -*- coding: utf-8 -*-
# -*- Channel PornoFlix -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

import re
import traceback
if not PY3: _dict = dict; from collections import OrderedDict as dict

from core.item import Item
from core import servertools
from core import scrapertools
from core import jsontools
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay
from lib.AlfaChannelHelper import DictionaryAdultChannel

IDIOMAS = {}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = []
list_quality_tvshow = []
list_servers = []
forced_proxy_opt = 'ProxySSL'

''' CANAL ANTIGUA OUT pages
    gameofporn  veporns  https://www.veporno.net  https://www.fxporn.net      http://www.veporns.com    '''

#  https://veporn.com/  https://pornoflix.com/

canonical = {
             'channel': 'pornoflix', 
             'host': config.get_setting("current_host", 'pornoflix', default=''), 
             'host_alt': ["https://pornoflix.com/"], 
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

finds = {'find': {'find_all': [{'tag': ['li'], 'class':['ficevi']}]},
         'categories': {'find_all': [{'tag': ['div', 'li'], 'class': ['taxonomy-item', 'performer-item']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+', '/page/%s/'], ['&page=\d+', '&page=%s']], 
         'last_page': dict([('find', [{'tag': ['ul', 'div'], 'class': ['page-numbers', 'pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], '@ARG': 'href', '@TEXT': 'page/(\d+)'}])]), 
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
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "?order=newest", curr_page=0, last_page=9999))
    itemlist.append(Item(channel=item.channel, title="Mas visto" , action="list_all", url=host + "?order=views", curr_page=0, last_page=9999))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=host + "?order=rating", curr_page=0, last_page=9999))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="list_all", url=host + "?order=comments", curr_page=0, last_page=9999))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=host + "?order=longest", curr_page=0, last_page=9999))
    itemlist.append(Item(channel=item.channel, title="Pornstars", action="section", url=host + "pornstar/", extra="Pornstar"))
    itemlist.append(Item(channel=item.channel, title="Categorias", action="section", url=host + "categories/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    return itemlist


def section(item):
    logger.info()

    findS = finds.copy()

    # if "Categorias" in item.title:
        # findS['controls']['cnt_tot'] = 999

    findS['url_replace'] = [['(\/[^$]+$)', r'\1?order=newest&page=1']]

    return AlfaChannel.section(item, finds=findS, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
   
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        try:
            
            elem_json['url'] = elem.get("href", '') or elem.a.get("href", '')
            elem_json['title'] = elem.a.get('data-mxptext', '') or elem.a.get('title', '') \
                                                                or (elem.img.get('alt', '') if elem.img else '') \
                                                                or elem.a.get_text(strip=True)
            if elem.img: elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                                                                     or elem.img.get('data-src', '') \
                                                                                     or elem.img.get('src', '')
            elem_json['cantidad'] = elem.find(class_=['count', 'number']).get_text(strip=True)
        
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

    if item.extra not in ["Pornstar", "Categorias", "Search"]:
        findS['controls'].update({'force_find_last_page': [0, 0, 'post']})
        findS['last_page'] = {}
        findS['next_page_rgx'] = [['&offset=\d+', '&offset=%s']]

    return AlfaChannel.list_all(item, finds=findS, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.a.get('title', '') \
                                 or elem.a.get_text(strip=True) \
                                 or (elem.img.get('alt', '') if elem.img else '')
            elem_json['thumbnail'] = elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') \
                                     or elem.img.get('src', '')
            elem_json['stime'] = elem.find('em', class_='time_thumb').get_text(strip=True)
            elem_json['quality'] = elem.find('div', title='Quality').get_text(strip=True) if elem.find('div', title='Quality') else ''
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        if not elem_json['url']: continue
        matches.append(elem_json.copy())
    
    # Paginado especial
    if item.extra not in ["Pornstar", "Categorias", "Search"]:
        item.url = AlfaChannel.doo_url                                          # host + wp-admin/admin-ajax.php
        item.post = 'action=action_load_video&offset=1'
    
    return matches


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def play(item):
    logger.info()

    itemlist = []
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    
    pornstars = soup.find_all('a', href=re.compile("/pornstar/[A-z0-9- ]+/"))
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
    lista = item.contentTitle.split('[/COLOR]')
    logger.debug(lista)
    pornstar = pornstar.replace('[/COLOR]', '')
    pornstar = ' %s' %pornstar
    lista.insert (1, pornstar)
    item.contentTitle = '[/COLOR]'.join(lista)
    
    url = soup.find('div', class_='video-container').iframe['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%s?s=%s&order=newest&page=1" % (host, texto.replace(" ", "+"))
    
    try:
        if texto:
            item.c_type = "search"
            item.extra="Search"
            item.texto = texto
            return list_all(item)
        else:
            return []
    
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
