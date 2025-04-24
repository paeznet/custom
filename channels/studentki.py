# -*- coding: utf-8 -*-
# -*- Channel studentki -*-
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

# https://sex-studentki.live/   https://ru.mult-porno.world/

canonical = {
             'channel': 'studentki', 
             'host': config.get_setting("current_host", 'studentki', default=''), 
             'host_alt': ["https://sex-studentki.live/"], 
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


finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['video']}]},     #'id': re.compile(r"^browse_\d+")}]},
         'categories': {'find_all': [{'tag': ['div'], 'class': ['category']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         # 'next_page': {},
         'next_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}, 
                                      {'tag': ['li'], 'class': ['selected']}]), 
                            ('find_next', [{'tag': ['li']},
                                           {'tag': ['a'], '@ARG': 'href'}]) ]),

         'next_page_rgx': [['?page=\d+', '?page=%s']], 
         'last_page': {}, 
         # 'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            # ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           # '@ARG': 'href', '@TEXT': '(?:/|=)(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {},
         # 'findvideos': dict([('find', [{'tag': ['li'], 'class': 'link-tabs-container', '@ARG': 'href'}]),
                             # ('find_all', [{'tag': ['a'], '@ARG': 'href'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            # 'list_all_stime': {'find': [{'tag': ['span'], 'class': ['is-hd'], '@TEXT': '(\d+:\d+)' }]},
                            # 'list_all_url': {'find': [{'tag': ['a'], 'class': ['link'], '@ARG': 'href'}]},
                            # 'list_all_stime': dict([('find', [{'tag': ['div'], 'class': ['time']}]),
                                                    # ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'list_all_quality': {'find': [{'tag': ['span', 'div'], 'class': ['hd'], '@ARG': 'class',  '@TEXT': '(hd)' }]},
                            # 'list_all_quality': dict([('find', [{'tag': ['span'], 'class': ['is-hd']}]),
                                                      # ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'list_all_premium': dict([('find', [{'tag': ['span'], 'class': ['ico-private']}]),
                                                       # ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'section_cantidad': dict([('find', [{'tag': ['span', 'div'], 'class': ['videos', 'column', 'rating', 'category-link-icon-videos']}]),
                                                      # ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(\d+)'}])])
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
    itemlist.append(Item(channel=item.channel, title="studentki" , action="submenu", url= "https://sex-studentki.live/", chanel="studentki", thumbnail = "https://sex-studentki.live/front/images/logo_ng_new.png"))
    itemlist.append(Item(channel=item.channel, title="rumult" , action="submenu", url= "https://ru.mult-porno.world/", chanel="rumult", thumbnail = "https://ru.mult-porno.world/front/images/logo1.png"))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    
    config.set_setting("current_host", item.url, item.chanel)
    AlfaChannel.host = item.url
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})


    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "videos/latest?page=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas Vistos" , action="list_all", url=item.url + "videos/popular?page=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "videos/feed?page=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Trending" , action="list_all", url=item.url + "videos/trending?page=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/", extra="Categorias", chanel=item.chanel))
    # itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))


    # if "24porn" in item.chanel:
        # itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "new-videos/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "best-videos/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "pornstars/", extra="PornStar", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "videos/1/", extra="Categorias", chanel=item.chanel))
    # if "bestpornstars" in item.chanel:
        # itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "new/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "best/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mas Caliente" , action="list_all", url=item.url + "trending/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/1/", extra="Categorias", chanel=item.chanel))
    # if "bigfuck" in item.chanel:
        # itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "recent/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "best/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mas Popular" , action="list_all", url=item.url + "most-popular/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "stars/1/", extra="PornStar", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "category/", extra="Categorias", chanel=item.chanel))
    # if "redporn" in item.chanel:
        # itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "new/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "best/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mas Caliente" , action="list_all", url=item.url + "trends/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "pornstars/1/", extra="PornStar", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "tubes/1/", extra="Categorias", chanel=item.chanel))
    # if "zzztube" in item.chanel:
        # itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "latest/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "best/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mas Caliente" , action="list_all", url=item.url + "hot/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "pornstars/1/", extra="PornStar", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/1/", extra="Categorias", chanel=item.chanel))
    
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=item.url + "channels/1/", extra="Canal", chanel=item.chanel))
    
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url, chanel=item.chanel))
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['([^$]+$)', r'\1/latest?page=1']]
    
    return AlfaChannel.section(item, finds=findS, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    soup = AHkwargs.get('soup', {})
    
    for elem in matches_int:
        
        elem_json = {}
        
        try:
            
            elem_json['url'] = elem.get("href", '') or elem.a.get("href", '')
            elem_json['title'] = elem.a.get("href", '').replace("/", "").replace("-", " ")
            # elem_json['title'] = elem.a.get('data-mxptext', '') or elem.a.get('title', '') \
                                                                # or (elem.img.get('alt', '') if elem.img else '') \
                                                                # or elem.a.get_text(strip=True)
            if elem.img: elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                                                                     or elem.img.get('data-src', '') \
                                                                                     or elem.img.get('src', '')
            if elem.find('div', class_=['badge-count']):
                elem_json['cantidad'] = elem.find('div', class_=['badge-count']).get_text(strip=True)
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        if not elem_json['url']: continue
        matches.append(elem_json.copy())
    return matches


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
            
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.a.get('title', '') \
                                 or elem.find(class_='title').get_text(strip=True) if elem.find(class_='title') else ''
            if not elem_json['title']:
                elem_json['title'] = elem.img.get('alt', '')
            
            elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') \
                                     or elem.img.get('src', '')
            elem_json['stime'] = elem.find(class_='column-time').get_text(strip=True) if elem.find(class_='column-time') else ''
            if not elem_json['stime'] and elem.find(string=re.compile('^([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$')):
                elem_json['stime'] = elem.find(string=re.compile('^([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$'))
            if elem.find('span', class_=['hd-thumbnail', 'is-hd']):
                elem_json['quality'] = elem.find('span', class_=['hd-thumbnail', 'is-hd']).get_text(strip=True)
            if elem.find('span', class_=['hd-thumbnail', 'is-hd', 'video_quality']):
                elem_json['quality'] = elem.find('span', class_=['hd-thumbnail', 'is-hd', 'video_quality']).get_text(strip=True)
            elem_json['premium'] = elem.find('i', class_='premiumIcon') \
                                     or elem.find('span', class_=['ico-private', 'premium-video-icon']) or ''
            elem_json['views'] = elem.find('span', class_='colum-views').get_text(strip=True)
            
            # if elem.find('a',class_='video_channel'):
                # elem_json['canal'] = elem.find('a',class_='video_channel').get_text(strip=True)
            
            pornstars = elem.find_all('div', class_="model-name")
            if pornstars:
                for x, value in enumerate(pornstars):
                    pornstars[x] = value.get_text(strip=True)
                elem_json['star'] = ' & '.join(pornstars)
            
            
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
    
    # if soup.find_all('a', href=re.compile("/модель/[A-z0-9-%20]+")):
        # pornstars = soup.find_all('a', href=re.compile("/модель/[A-z0-9-%20]+"))
        
        # for x, value in enumerate(pornstars):
            # pornstars[x] = value.get_text(strip=True)
        
        # pornstar = ' & '.join(pornstars)
        # pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        # logger.debug(pornstar)
        # lista = item.contentTitle.split('[/COLOR]')
        # pornstar = pornstar.replace('[/COLOR]', '')
        # pornstar = ' %s' %pornstar
        # if AlfaChannel.color_setting.get('quality', '') in item.contentTitle:
            # lista.insert (2, pornstar)
        # else:
            # lista.insert (1, pornstar)
        # item.contentTitle = '[/COLOR]'.join(lista)
    
    url = soup.video
    if url:
        url = url.source['src']
        url += "|Referer=%s" % item.url
    itemlist.append(Item(channel=item.channel, action="play",  contentTitle = item.contentTitle, url=url))
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch?q=%s&page=1" % (item.url, texto.replace(" ", "+"))
    
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
