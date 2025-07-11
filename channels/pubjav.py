# -*- coding: utf-8 -*-
# -*- Channel PubJav -*-
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

###      https://sextb.net/  https://sextb.xyz/     mismo contenido y casi estructura

canonical = {
             'channel': 'pubjav', 
             'host': config.get_setting("current_host", 'pubjav', default=''), 
             'host_alt': ["https://pubjav.com/"], 
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

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['ml-item']}]},     #'id': re.compile(r"^browse_\d+")}]},
         'categories': {'find_all': [{'tag': ['div'], 'class': ['col-md-2']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['&pg=\d+', '&pg=%s'], ['\pg-\d+', '\pg-%s']], 
         'last_page': dict([('find', [{'tag': ['ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': '(\d+)'}])]), #(:?pg=|pg-)
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['div', 'li'], 'class': ['fakeplayer', 'switch-source']}]}, 
         # 'findvideos': dict([('find', [{'tag': ['ul'], 'class': ['server-list']}]),
                             # ('find_all', [{'tag': ['li']}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'section_cantidad': dict([('find', [{'tag': ['div'], 'class': ['count']}]),
                                                      ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(\d+)'}])])
                           },
         'controls': {'url_base64': False, 'cnt_tot': 24, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)

api = "https://pubjav.com/movies?genre=%s&quality=all&year=all&sort=%s&pg=1"

def mainlist(item):
    logger.info()
    itemlist = []
    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=api %("all","desc")))
    itemlist.append(Item(channel=item.channel, title="Mas Vistos" , action="list_all", url=api %("all","viewed")))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=api %("all","liked")))
    itemlist.append(Item(channel=item.channel, title="Favoritos" , action="list_all", url=api %("all","favorite")))
    itemlist.append(Item(channel=item.channel, title="Release" , action="list_all", url=api %("all","release")))
    itemlist.append(Item(channel=item.channel, title="Censurado" , action="list_all", url=api %("censored","desc")))
    itemlist.append(Item(channel=item.channel, title="Sin Censura" , action="list_all", url=api %("uncensored","desc")))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "studios", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "actors", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "genres", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:genre|studio|actor)\/[^$]+$)', r'\1?genre=all&quality=all&year=all&sort=desc&pg=1']]
    
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
            
            trailer = elem.find('a', class_='mli-trailer')
            tit1 = trailer['data-title']
            tit2 = elem.h2.text.strip()
            elem_json['thumbnail'] = trailer.get('data-poster', '') or elem.img.get('data-original', '')
            elem_json['title'] = "%s %s" %(tit1,tit2)
            
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
    srv_ids = {"Vs": "Voe",
               "Vg": "Vidguard",
               "Tb": "Emturbovid",
               "Sw": "Streamwish",
               "Dd": "Doodstream",
               "St": "Streamtape",
               "Su": "bestb",
               # "Us": "https://player.upn.one/#urh1y",
               "Fl": "Vidhidepro"
               }
    
    
    soup = AHkwargs.get('soup', {}).find('div', class_='mvic-desc')
    canal = soup.find('a', href=re.compile("/studio/[A-z0-9-]+"))['title']
    if soup.find_all('a', href=re.compile("/actor/[A-z0-9-]+")):
        pornstars = soup.find_all('a', href=re.compile("/actor/[A-z0-9-]+"))
        
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        item.plot = "Estudio: %s \nActores: %s" %(canal,pornstar)
    
    
    for elem in matches_int:
        elem_json = {}
        try:
            src = elem.get("data-source", "")
            id = elem.get("data-id", "") or elem.get("data-episode", "")
            if len(matches_int) > 1 and not id: #quita fakeplayer cuando hay servers 
                continue
            elem_json['post']= "episode=%s&filmId=%s" %(id,src)
            elem_json['url'] = item.url
            elem_json['server'] = elem.get_text(strip=True).capitalize()
            if elem_json['server'] in ["Us", "trailer"]: continue
            if elem_json['server'] in srv_ids:
                elem_json['server'] = srv_ids[elem_json['server']]
            elem_json['language'] = ''
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())

        if not elem_json.get('url', ''): continue
        matches.append(elem_json.copy())

    return matches, langs


def play(item):
    logger.info()
    
    itemlist = []
    
    post_url = "%sajax/player" %host
    soup = AlfaChannel.create_soup(post_url, post=item.post, **kwargs)
    data = str(soup).replace("'\\", "").replace("\/", "/").replace("\\", "")
    url = scrapertools.find_single_match(data, 'src="([^"]+)"')
    if "Streamwish" in item.server or "Vidhidepro" in item.server: ###  or "Emturbovid" in item.server
        url += "|Referer=%s" %host
    itemlist.append(Item(channel=item.channel, action="play", server= item.server, contentTitle = item.contentTitle, url=url))
    
    # itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/%s/pg-1" % (host, texto.replace(" ", "-"))
    
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
