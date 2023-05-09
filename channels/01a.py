# -*- coding: utf-8 -*-
# -*- Channel PornVase -*-
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

canonical = {
             'channel': 'eporner', 
             'host': config.get_setting("current_host", 'eporner', default=''), 
             'host_alt': ["https://www.eporner.com/"], 
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

finds = {'find': {'find_all': [{'tag': ['div'], 'id': re.compile(r"^vf\d+")}]},
         'categories': {'find_all': [{'tag': ['div'], 'class': ['categoriesbox', 'mbprofile']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['div'], 'class': ['numlist2']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]), 
         'next_page_rgx': [['\/\d+\/', '/%s/']], 
         'last_page': {}, 
         # 'next_page_rgx': [['&from_videos=\d+', '&from_videos=%s'], ['&from=\d+', '&from=%s']], 
         # 'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            # ('find_all', [{'tag': ['a'], 'string': re.compile('(?i)(?:ltima|last)'), '@POS': [-1], 
                                           # '@ARG': 'data-parameters', '@TEXT': 'from\w*:\s*(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {}, 
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'controls': {'url_base64': False, 'cnt_tot': 24, 'reverse': False, 'profile': 'default'}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    
    itemlist = []
    
    # itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=host + "más-reciente/?sort_by=post_date&from=1"))
    # itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="list_all", url=host + "más-visto/?sort_by=video_viewed_month&from=1"))
    # itemlist.append(Item(channel=item.channel, title="Mejor valorada" , action="list_all", url=host + "mejor-valorado/?sort_by=rating_month&from=1"))
    # itemlist.append(Item(channel=item.channel, title="Pornstar" , action="section", url=host + "models/?sort_by=total_videos&from=1", extra="Pornstar"))
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host, extra="Canal"))
    # itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "categorías/?sort_by=title&from=1", extra="Categorias"))
    # itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    itemlist.append(Item(channel=item.channel, title="Nuevos", action="list_all", url=host + "0/"))
    itemlist.append(Item(channel=item.channel, title="Más visto", action="list_all", url=host + "most-viewed/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado", action="list_all", url=host + "top-rated/"))
    itemlist.append(Item(channel=item.channel, title="Pornstars", action="section", url=host + "pornstar-list/"))
    itemlist.append(Item(channel=item.channel, title="Categorias", action="section", url=host + "cats/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    
    findS['url_replace'] = [['(\/(?:categories|channels|сanales|models|pornstars)\/[^$]+$)', r'\1?sort_by=post_date&from=1']]
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


# def section(item):
    # logger.info()
    
    # findS = finds.copy()
    # findS['url_replace'] = [['(\/(?:categories|channels|models|pornstars)\/[^$]+$)', r'\1?sort_by=post_date&from=1']]
    
    # if item.extra == 'Pornstar':
        # findS['categories'] = dict([('find', [{'tag': ['div'], 'class': 'list-models'}]), 
                                    # ('find_all', [{'tag': ['a'], 'class': 'item'}])])
    
    # if item.extra == 'Canal':
        # findS['categories'] = dict([('find', [{'tag': ['div'], 'id': 'popup-sponsors'}]), 
                                    # ('find_all', [{'tag': ['li']}])])
        # findS['last_page'] = {}
    
    # if item.extra == 'Categorias':
        # findS['categories'] = dict([('find', [{'tag': ['div'], 'class': 'list-categories'}]), 
                                    # ('find_all', [{'tag': ['a']}])])
    # return AlfaChannel.section(item, finds=findS, **kwargs


def list_all(item):
    logger.info()
    
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
            elem_json['title'] = elem.find('p', class_='mbtit').get_text(strip=True)
            elem_json['thumbnail'] = elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') \
                                     or elem.img.get('src', '')
            elem_json['stime'] = elem.find('span', class_='mbtim').get_text(strip=True) if elem.find('span', class_='mbtim') else ''
            elem_json['quality'] = elem.find('div', title='Quality').get_text(strip=True) if elem.find('div', title='Quality') else ''
            if elem.find('span', class_='mbvie'):
                elem_json['views'] = elem.find('span', class_='mbvie').get_text(strip=True)
            #elem_json['action'] = 'findvideos'
        
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
    
    # item.url = "%sbuscar/?q=%s&sort_by=video_viewed&from_videos=1" % (host, texto.replace(" ", "+"))
    item.url = "%ssearch/%s/" % (host, texto.replace(" ", "-"))
    
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
