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

################   FALLAN FOTOS  Failed: HTTP response code said error(22)

canonical = {
             'channel': 'xxvideoss', 
             'host': config.get_setting("current_host", 'xxvideoss', default=''), 
             'host_alt': ["https://xxvideoss.org/"], 
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

finds = {'find': dict([('find', [{'tag': ['main'], 'id': ['main']}]),
                       ('find_all', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}])]),
         'categories': dict([('find', [{'tag': ['main'], 'id': ['main']}]),
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
    itemlist.append(Item(channel = item.channel, title="Canal" , action="section", url=host + "legal-notice/", extra="Canal"))
    itemlist.append(Item(channel = item.channel, title="Categorias" , action="section", url=host + "most-popular-adult-video-categories/", extra="Categorias"))
    itemlist.append(Item(channel = item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    # if "Categorias" in item.extra:
        # findS['categories'] = dict([('find', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}]),
                                    # ('find_all', [{'tag': ['a']}])])
    if "Canal" in item.extra:
        findS['categories'] = dict([('find', [{'tag': ['aside'], 'id': ['block-23']}]),
                                    ('find_all', [{'tag': ['a']}])])
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    findS['controls']['action'] = 'findvideos'
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)
    # return AlfaChannel.list_all(item, finds=findS, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    # ''' Carga desde AHkwargs la clave “matches” resultado de la ejecución del “profile=default” en AH. 
    # En “matches_int” sigue pasando los valores de siempre. '''
    # matches_org = AHkwargs.get('matches', [])
    # findS = AHkwargs.get('finds', finds)
    # ''' contador para asegurar que matches_int y matches_org van sincronizados'''
    # x = 0
    
    #############################################   TEST ###############################################
    soup = AHkwargs.get('soup', {})
    # logger.debug(soup)
    # matches = soup.find_all('li', id=re.compile(r"^browse_\d+"))
    logger.debug(soup.find_all('li', id=re.compile(r"^browse_\d+")))
    
    matches_org = AHkwargs.get('matches', [])
    logger.debug("=================== findS ==========================")
    logger.debug(findS)
    # logger.debug("=========== matches_int & _org =====================")
    # logger.debug(matches_int)
    # logger.debug(matches_org)
    logger.debug("=================== elem1 ==========================")
    logger.debug(matches_int[0])
    logger.debug(matches_org[0])
    logger.debug("====================================================")
    logger.debug(matches_int[0].a.get('title', ''))
    logger.debug("elem_json['title'] = "+ matches_org[0].get('title', ''))
    
    ######################################################################################################
    
    
    for elem in matches_int:
        
        elem_json = {}
        # '''carga el valor del json que ya viene procesado del “profile=default” en AH'''
        # elem_json = matches_org[x].copy() if x+1 <= len(matches_org) else {}
        
        try:
            # if 'livecam' in elem.get("class", []): continue   ###  Excepcion pornone para quitar los item livecams

            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.a.get('title', '') \
                                 or elem.find(class_='title').get_text(strip=True) if elem.find(class_='title') else ''
            if not elem_json['title']:
                elem_json['title'] = elem.img.get('alt', '')
            
            
            thumbnail = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                        or elem.img.get('data-src', '') \
                        or elem.img.get('src', '')
            # thumbnail += "|Referer=%s" %host
            # thumbnail += "|verifypeer=false"
            # thumbnail += "|ignore_response_code=True" 
            # headers = AlfaChannel.httptools.default_headers.copy()
            # logger.debug(headers)
            # if PY3:
                # from urllib.parse import urlparse
            # else:
                # from urlparse import urlparse 
            # thumbnail += "|%s&Referer=%s/&Origin=%s" % (urlparse.urlencode(headers), host,host)
            elem_json['thumbnail'] = thumbnail.replace("-620x383", "")
            # elem_json['thumbnail'] = thumbnail
            logger.debug(elem_json['thumbnail'])
            elem_json['stime'] = elem.find(class_='duration').get_text(strip=True) if elem.find(class_='duration') else ''
            # if not elem_json['stime'] and elem.find(text=lambda text: isinstance(text, self.Comment) \
                                      # and 'duration' in text):
                # elem_json['stime'] = self.do_soup(elem.find(text=lambda text: isinstance(text, self.Comment) \
                                                  # and 'duration' in text)).find(class_='duration').get_text(strip=True)
            # if not elem_json['stime'] and elem.find(string=re.compile('^([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$')):
                # elem_json['stime'] = elem.find(string=re.compile('^([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$'))
            # if elem.find('span', class_=['hd-thumbnail', 'is-hd']):
                # elem_json['quality'] = elem.find('span', class_=['hd-thumbnail', 'is-hd']).get_text(strip=True)
            # if elem.find('span', class_=['hd-thumbnail', 'is-hd', 'video_quality']):
                # elem_json['quality'] = elem.find('span', class_=['hd-thumbnail', 'is-hd', 'video_quality']).get_text(strip=True)
            # elem_json['stime'] = elem_json['stime'].replace(elem_json['quality'], '')
            # elif elem.find(text=lambda text: isinstance(text, self.Comment) and 'hd' in text):
                # elem_json['quality'] = 'HD'
            # elem_json['premium'] = elem.find('i', class_='premiumIcon') \
                                     # or elem.find('span', class_='ico-private') or ''
            elem_json['premium'] = elem.find('i', class_='premiumIcon') \
                                     or elem.find('span', class_=['ico-private', 'premium-video-icon']) or ''

            if elem.find('div', class_='videoDetailsBlock') \
                                     and elem.find('div', class_='videoDetailsBlock').find('span', class_='views'):
                elem_json['views'] = elem.find('div', class_='videoDetailsBlock')\
                                    .find('span', class_='views').get_text('|', strip=True).split('|')[0]
            # elif elem.find('div', class_='views'):
                # elem_json['views'] = elem.find('div', class_='views').get_text(strip=True) 
            elif elem.find('span', class_='video_count'):
                elem_json['views'] = elem.find('span', class_='video_count').get_text(strip=True)
            
            
            # if elem.find('a',class_='video_channel'):
                # elem_json['canal'] = elem.find('a',class_='video_channel').get_text(strip=True)
            # pornstars = elem.find_all('li', class_="pstar")
            # if pornstars:
                # for x, value in enumerate(pornstars):
                    # pornstars[x] = value.get_text(strip=True)
                # elem_json['star'] = ' & '.join(pornstars)
            
            # '''Pasar por findvideos '''
            # elem_json['action'] = 'findvideos'
            
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        if not elem_json['url']: continue
        matches.append(elem_json.copy())
        # '''filtros que deben coincidir con los que tiene el “profile=default” en AH para que no descuadren las dos listas'''
        # if not elem.a.get('href', ''): continue 
        
        # '''guarda json modificado '''
        # matches.append(elem_json.copy())
        # '''se suma al contador de registros procesados VÁLIDOS'''
        # x += 1
        
        ###########  Paginado en absoluporn  donde tengo numero total de videos y consigo last_page
    # soup = AHkwargs.get('soup', {})
    # if AlfaChannel.last_page in [9999, 99999] and soup and soup.find('div', class_='pagination-nbpage'): 
        # total = soup.find('div', class_='pagination-nbpage').find('span', class_='text1').get_text(strip=True)
        # total = scrapertools.unescape(total).split(' ')[-2]
        # AlfaChannel.last_page = int(int(total) / finds['controls'].get('cnt_tot', 30))
        # logger.error(AlfaChannel.last_page)
        
    # logger.debug(matches)
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
