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

#  https://www.porntube.com    https://www.pornerbros.com   https://www.4tube.com  https://www.fux.com
canonical = {
             'channel': '4tube', 
             'host': config.get_setting("current_host", '4tube', default=''), 
             'host_alt': ["https://www.4tube.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
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

# {'find_all': [{'tag': ['div'], 'class': 'thumb_video'}]},



finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['video_list']}]),
                       ('find_all', [{'tag': ['div'], 'class': 'thumb_video'}])]),
         'categories': {'find_all': [{'tag': ['a'], 'class': 'thumb-link'}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['ul'], 'class': ['pagination']}]),
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]), 
         
         # 'next_page': {},
         'next_page_rgx': [['\/page\/\d+\/', '/page/%s/']], 
         # 'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            # ('find_all', [{'tag': ['a'], 'string': re.compile('(?i)(?:ltima|last)'), '@POS': [-1], 
                                           # '@ARG': 'href', '@TEXT': 'page/(\d+)'}])]), 
         'last_page': {},
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
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "videos?sort=date"))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="list_all", url=host + "videos?time=month"))
    itemlist.append(Item(channel=item.channel, title="Mas Visto" , action="list_all", url=host + "videos?sort=views&time=month"))
    itemlist.append(Item(channel=item.channel, title="Mas Valorada" , action="list_all", url=host + "videos?sort=rating&time=month"))
    itemlist.append(Item(channel=item.channel, title="Longitud" , action="list_all", url=host + "videos?sort=duration&time=month"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="categorias", url=host + "pornstars", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "channels", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "tags", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url= host))
    
    itemlist.append(Item(channel=item.channel, title = ""))
    itemlist.append(Item(channel=item.channel, title="Trans", action="submenu", orientation="shemale/"))
    itemlist.append(Item(channel=item.channel, title="Gay", action="submenu", orientation="gay/"))
    
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    url = host + item.orientation
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=url + "videos?sort=date"))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="list_all", url=url + "videos?time=month"))
    itemlist.append(Item(channel=item.channel, title="Mas Visto" , action="list_all", url=url + "videos?sort=views&time=month"))
    itemlist.append(Item(channel=item.channel, title="Mas Valorada" , action="list_all", url=url + "videos?sort=rating&time=month"))
    itemlist.append(Item(channel=item.channel, title="Longitud" , action="list_all", url=url + "videos?sort=duration&time=month"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="categorias", url=url + "pornstars", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=url + "channels", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=url + "tags", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=url))
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    
    findS['url_replace'] = [['(\/(?:categories|channels|сanales|models|pornstars)\/[^$]+$)', r'\1?sort_by=post_date&from=1']]
    
    # return AlfaChannel.section(item, finds=findS, **kwargs)
    return AlfaChannel.section(item, finds=findS, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
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
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    # logger.debug(soup)
    # matches = soup.find_all('li', id=re.compile(r"^browse_\d+"))
    logger.debug(soup.find_all('li', class_='category_item'))

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
        
        
        
        # matches = soup.find_all('a', class_='thumb-link')
        # for elem in matches:
            # url = elem['href']
            # title = elem['title']
            # thumbnail = elem.img['data-original']
            # cantidad = elem.find('div', class_='thumb-info').li
            # if cantidad:
                # title = "%s (%s)" % (title,cantidad.text.strip())
        
        try:
            
            elem_json['url'] = elem.get("href", '')
            elem_json['title'] = elem.get('title', '')
            elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                                                        or elem.img.get('data-src', '') \
                                                                        or elem.img.get('src', '')
            if elem.find('div', class_=['thumb-info']).li:
                elem_json['cantidad'] = elem.find('div', class_=['thumb-info']).li.get_text(strip=True)
            # elif elem.find('div', class_='videos'):
                # elem_json['cantidad'] = elem.find('div', class_='videos').get_text(strip=True)
            # elif elem.find(string=re.compile(r"(?i)videos|movies")):
                # elem_json['cantidad'] = elem.find(string=re.compile(r"(?i)videos|movies")).strip()
                # logger.debug(elem_json['cantidad'].strip())
            # elif elem.find(string='Videos'):
                # elem_json['cantidad'] = elem.find(string='Videos').get_text(strip=True)
            # if not elem_json.get('cantidad') and elem.find(text=lambda text: isinstance(text, self.Comment) \
                                              # and 'videos' in text):
                # elem_json['cantidad'] = self.do_soup(elem.find(text=lambda text: isinstance(text, self.Comment) \
                                                     # and 'videos' in text)).find(class_='videos').get_text(strip=True)

        
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
    
    # logger.debug(matches)
    return matches


def list_all(item):
    logger.info()
    
    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()
    
    matches = []
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        logger.debug(elem)
        elem_json = {}
        
        try:
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.a.get('title', '')
            elem_json['thumbnail'] = elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') \
                                     or elem.img.get('src', '')
            elem_json['stime'] = elem.find('li', class_='duration-top').get_text(strip=True)
            elem_json['quality'] = elem.find('li', class_='topHD').get_text(strip=True)
            pornstars = elem.find_all('li', class_="master-pornstar")
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
    if soup.find('ul', class_='pornlist'):
        pornstars = soup.find('ul', class_='pornlist').find_all('h3')
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        pornstar = ' & '.join(pornstars)
        color = AlfaChannel.color_setting.get('rating_3', '')
        txt = scrapertools.find_single_match(item.contentTitle, "%s\]([^\[]+)"  % color)
        if not txt.lower() in pornstar.lower():
            pornstar = "%s & %s" %(txt,pornstar)
        item.contentTitle = re.sub(r"%s][^\[]+"  % color, "%s]{0}".format(pornstar) % color, item.contentTitle)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch?sort=date&q=%s" % (item.url, texto.replace(" ", "-"))
    
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
