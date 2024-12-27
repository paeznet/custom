# -*- coding: utf-8 -*-
# -*- Channel AmigosPorn -*-
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

canonical = {
             'channel': 'amigosporn', 
             'host': config.get_setting("current_host", 'amigosporn', default=''), 
             'host_alt': ["https://amigosporn.com/"], 
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
         'categories': {'find_all': [{'tag': ['a'], 'class': ['ttw-term-link']}]},
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['nav'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': 'page(?:/|=)(\d+)'}])]), 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['div'], 'class': ['video_box']}]),
                             ('find_all', [{'tag': ['button'], '@ARG': 'value'}])]),
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
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "page/1/"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="submenu", url=host + "actress/", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "category/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    
    matches = soup.find_all('li', attrs={"data-letter": re.compile(r"^\w")})
    for elem in matches:
        title = elem.a.get_text(strip=True)
        id = elem.a['href'].replace("#", "")
        itemlist.append(Item(channel=item.channel, title=title, id=id , action="section", url=item.url, extra="Abc"))
    
    return itemlist

def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:category|actress)\/[^$]+$)', r'\1page/1/']]
    
    if item.extra == 'Abc':
        findS['categories'] =  dict([('find', [{'tag': ['div'], 'id': ['%s' %item.id]}]),
                                     ('find_all', [{'tag': ['span'], 'class': ['tag-groups-tag']}])])
        findS['profile_labels']['section_title'] = dict([('find', [{'tag': ['a']}]),
                                                         ('get_text', [{'tag': '', 'strip': True}])])
        findS['profile_labels']['section_cantidad'] = {'find': [{'tag': 'a', '@ARG': 'title', '@TEXT': '(\d+)'}]}
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    findS['controls']['action'] = 'findvideos'
    
    return AlfaChannel.list_all(item, finds=findS, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        
        elem_json = {}
        
        try:
            elem_json['url'] = elem.a.get('href', '')
            img = elem.a.get('style', '')
            elem_json['thumbnail'] =  scrapertools.find_single_match(img, "'([^']+)'")
            
            title = elem.h2.get_text(strip=True)
            texto = elem['class']
            pornstars = []
            for txt in texto:
                if "studio-" in txt:
                    canal = txt.replace("studio-", "").capitalize()
                    canal = canal.replace("Onlyfans", "OnlyFans")
                    elem_json['canal'] = canal
                    title = title.replace(canal, "")
                if "actress-" in txt:
                    txt = txt.replace("actress-", ""). replace("-", " ").title()
                    pornstars.append(txt)
                    elem_json['star'] = ' & '.join(pornstars)
                    for elem in pornstars:
                        title = title.replace(elem, "")
                        
            elem_json['title'] = title
        
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
            elem_json['url'] = elem
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
