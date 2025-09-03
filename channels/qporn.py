# -*- coding: utf-8 -*-
# -*- Channel qporn -*-
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

# https://24porn.com/   https://bigfuck.tv/  https://bestpornstars.xxx/
# https://redporn.porn/  https://zzztube.tv/
# 

canonical = {
             'channel': 'qporn', 
             'host': config.get_setting("current_host", 'qporn', default=''), 
             'host_alt': ["https://qporn.org/"], 
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


#     https://5porn.net  https://pornj.net/
# ORG :  https://pornf.org/  https://pornh.org/  https://pornv.org/ https://pornq.org/ 
       # https://porn2.org/ , 3, 5, 6, L,     
       # https://qporn.org/   https://bporn.org/  https://cporn.org/  https://fporn.org/ 
       # https://hporn.org/  https://kporn.org/  https://lporn.org/  https://pporn.org/ 
       # https://rporn.org/  https://7porn.org/ https://0porn.org/ , y, 
 #  https://yporn.info/ , 0, 5, 6, 9, q, s, z
 #  https://pornq.info/  https://pornf.info/ , 3, 4, 5, 6, 7, 8 , b, c, d, e, f, g, i, j, l, m, t, z
 #  

finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['videos']}]),
                       ('find_all', [{'tag': ['article']}])]),
         'categories': dict([('find', [{'tag': ['div', 'ul'], 'class': ['videos', 'cat']}]),
                             ('find_all', [{'tag': ['article', 'li']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['div', 'ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], 'string': re.compile('(?i)(?:more|next)'), '@POS': [-1], '@ARG': 'href'}])]),
         'next_page_rgx': [['\?page=\d+', 'next_page_url']], 
         'last_page':  {},
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['li'], 'class': 'link-tabs-container', '@ARG': 'href'}]),
                             ('find_all', [{'tag': ['a'], '@ARG': 'href'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'section_cantidad': dict([('find', [{'tag': ['span']}]),
                                                      ('get_text', [{'strip': True}])])
                           },
         'controls': {'url_base64': False, 'cnt_tot': 32, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="qporn" , action="submenu", url= "https://qporn.org/", chanel="24porn", thumbnail = "https://i.postimg.cc/VLBthgzb/qporn.png"))
    itemlist.append(Item(channel=item.channel, title="bporn" , action="submenu", url= "https://bporn.org/", chanel="bporn", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="cporn" , action="submenu", url= "https://cporn.org/", chanel="cporn", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="fporn" , action="submenu", url= "https://fporn.org/", chanel="fporn", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="hporn" , action="submenu", url= "https://hporn.org/", chanel="hporn", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="kporn" , action="submenu", url= "https://kporn.org/", chanel="kporn", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="lporn" , action="submenu", url= "https://lporn.org/", chanel="lporn", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="pporn" , action="submenu", url= "https://pporn.org/", chanel="pporn", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="rporn" , action="submenu", url= "https://rporn.org/", chanel="rporn", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="yporn" , action="submenu", url= "https://yporn.org/", chanel="yporn", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="0porn" , action="submenu", url= "https://0porn.org/", chanel="0porn", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="7porn" , action="submenu", url= "https://7porn.org/", chanel="7porn", thumbnail = ""))
    
    itemlist.append(Item(channel=item.channel, title="pornq" , action="submenu", url= "https://pornq.info/", chanel="pornq", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="pornb" , action="submenu", url= "https://pornb.info/", chanel="pornb", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="pornc" , action="submenu", url= "https://pornc.info/", chanel="pornc", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="pornd" , action="submenu", url= "https://pornd.info/", chanel="pornd", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="porne" , action="submenu", url= "https://porne.info/", chanel="porne", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="pornf" , action="submenu", url= "https://pornf.info/", chanel="pornf", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="porng" , action="submenu", url= "https://porng.info/", chanel="porng", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="porni" , action="submenu", url= "https://porni.info/", chanel="porni", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="pornj" , action="submenu", url= "https://pornj.info/", chanel="pornj", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="pornl" , action="submenu", url= "https://pornl.info/", chanel="pornl", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="pornm" , action="submenu", url= "https://pornm.info/", chanel="pornm", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="pornt" , action="submenu", url= "https://pornt.info/", chanel="pornt", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="pornz" , action="submenu", url= "https://pornz.info/", chanel="pornz", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="porn3" , action="submenu", url= "https://porn3.info/", chanel="porn3", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="porn4" , action="submenu", url= "https://porn4.info/", chanel="porn4", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="porn5" , action="submenu", url= "https://porn5.info/", chanel="porn5", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="porn6" , action="submenu", url= "https://porn6.info/", chanel="porn6", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="porn7" , action="submenu", url= "https://porn7.info/", chanel="porn7", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="porn8" , action="submenu", url= "https://porn8.info/", chanel="porn8", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="porn9" , action="submenu", url= "https://porn9.info/", chanel="porn9", thumbnail = ""))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    
    config.set_setting("current_host", item.url, item.chanel)
    AlfaChannel.host = item.url
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "?page=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas visto" , action="list_all", url=item.url + "?page=1&o=views", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="list_all", url=item.url + "?page=1&o=popular", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "?page=1&o=loves", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=item.url + "?page=1&o=duration", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=item.url + "channels?page=1&o=popular", extra="Canal", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "pornstars?page=1&o=popular", extra="PornStar", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories", extra="Categorias", chanel=item.chanel))
    
    
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url, chanel=item.chanel))
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['([^$]+$)', r'\1?page=1']]
    findS['controls']['cnt_tot'] = 60
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.a.get('title', '')
            elem_json['thumbnail'] = elem.img.get('src', '')
            id = elem.figure['id']
            url = "cdn/%s.m3u8|Referer=%s" %(id, item.url)
            elem_json['url'] =AlfaChannel.urljoin(AlfaChannel.host,url)
            
            elem_json['stime'] = elem.i.get('data-text', '')
            if elem.find('figure', class_=['hd']):
                elem_json['quality'] = "HD"
            
            if elem.find('div', class_='videoDetailsBlock') \
                                     and elem.find('div', class_='videoDetailsBlock').find('span', class_='views'):
                elem_json['views'] = elem.find('div', class_='videoDetailsBlock')\
                                    .find('span', class_='views').get_text('|', strip=True).split('|')[0]
            
            elif elem.find('span', class_='video_count'):
                elem_json['views'] = elem.find('span', class_='video_count').get_text(strip=True)
            
            if elem.find('a',class_='video_channel'):
                elem_json['canal'] = elem.find('a',class_='video_channel').get_text(strip=True)
            pornstars = elem.find_all('a', href=re.compile("/pornstar/[A-z0-9-]+"))
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


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/%s?page=1" % (item.url, texto.replace(" ", "+"))
    
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
