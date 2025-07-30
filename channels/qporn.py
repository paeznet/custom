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

####  PAGINACION?

# https://0porn.org/  https://0porn.info/  https://5porn.net   https://5porn.info  https://6porn.info  
# https://porn4.info/
# ORG :  https://pornh.org/  https://pornq.org/  https://pornv.org/ https://pornq.org/ porn e,
       # https://7porn.org/ https://cporn.org/  https://fporn.org/ https://hporn.org/  https://kporn.org/ 
       # https://bporn.org/ https://cporn.org/  https://fporn.org/ https://hporn.org/  https://kporn.org/ 
       # https://lporn.org/ https://pporn.org/ https://qporn.org/   https://rporn.org/
 #  https://pornq.info/

finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['videos']}]),
                       ('find_all', [{'tag': ['article']}])]),
         'categories': dict([('find', [{'tag': ['div', 'ul'], 'class': ['videos', 'cat']}]),
                             ('find_all', [{'tag': ['article', 'li']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         # 'next_page': {'find': [{'tag': ['a'], 'string': re.compile('(?i)(?:more|next)'), '@ARG': 'href'}]}, #### COGE blog que tiene more
         'next_page': dict([('find', [{'tag': ['div', 'ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], 'string': re.compile('(?i)(?:more|next)'), '@POS': [-1], '@ARG': 'href'}])]),
         # 'next_page_rgx': [['\?page=\d+', 'next_page_url'], ['\?page=\d+&o=[a-z]+', 'next_page_url']], 
         'next_page_rgx': [['\?page=\d+', 'next_page_url']], 
         'last_page':  {},
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['li'], 'class': 'link-tabs-container', '@ARG': 'href'}]),
                             ('find_all', [{'tag': ['a'], '@ARG': 'href'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            # 'list_all_quality': dict([('find', [{'tag': ['div'], 'class': ['b-thumb-item__detail']}]),
                                                      # ('get_text', [{'strip': True}])]),
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
    itemlist.append(Item(channel=item.channel, title="kporn" , action="submenu", url= "https://kporn.org/", chanel="kporn", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="lporn" , action="submenu", url= "https://lporn.org/", chanel="lporn", thumbnail = ""))
    itemlist.append(Item(channel=item.channel, title="rporn" , action="submenu", url= "https://rporn.org/", chanel="rporn", thumbnail = ""))
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
    
    # return AlfaChannel.list_all(item, **kwargs)
    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


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
    # logger.debug(soup.find('div', class_='pagination').find('a', string=re.compile("(?i)(?:more|next)")))
    
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
            elem_json['title'] = elem.a.get('title', '') #\
                                 # or elem.find(class_='title').get_text(strip=True) if elem.find(class_='title') else ''
            # if not elem_json['title']:
                # elem_json['title'] = elem.img.get('alt', '')
            
            elem_json['thumbnail'] = elem.img.get('src', '')
            id = elem.figure['id']
            # url = "cdn/%s.mp4" %id
            url = "cdn/%s.m3u8|Referer=%s" %(id, item.url)
            elem_json['url'] =AlfaChannel.urljoin(AlfaChannel.host,url)
            
            elem_json['stime'] = elem.i.get('data-text', '')
            # if not elem_json['stime'] and elem.find(text=lambda text: isinstance(text, self.Comment) \
                                      # and 'duration' in text):
                # elem_json['stime'] = self.do_soup(elem.find(text=lambda text: isinstance(text, self.Comment) \
                                                  # and 'duration' in text)).find(class_='duration').get_text(strip=True)
            # if not elem_json['stime'] and elem.find(string=re.compile('^([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$')):
                # elem_json['stime'] = elem.find(string=re.compile('^([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$'))
            if elem.find('figure', class_=['hd']):
                elem_json['quality'] = "HD"
            # if elem.find('span', class_=['hd-thumbnail', 'is-hd', 'video_quality']):
                # elem_json['quality'] = elem.find('span', class_=['hd-thumbnail', 'is-hd', 'video_quality']).get_text(strip=True)
            # elem_json['stime'] = elem_json['stime'].replace(elem_json['quality'], '')
            # elif elem.find(text=lambda text: isinstance(text, self.Comment) and 'hd' in text):
                # elem_json['quality'] = 'HD'
            # elem_json['premium'] = elem.find('i', class_='premiumIcon') \
                                     # or elem.find('span', class_='ico-private') or ''
            # elem_json['premium'] = elem.find('i', class_='premiumIcon') \
                                     # or elem.find('span', class_=['ico-private', 'premium-video-icon']) or ''

            if elem.find('div', class_='videoDetailsBlock') \
                                     and elem.find('div', class_='videoDetailsBlock').find('span', class_='views'):
                elem_json['views'] = elem.find('div', class_='videoDetailsBlock')\
                                    .find('span', class_='views').get_text('|', strip=True).split('|')[0]
            # elif elem.find('div', class_='views'):
                # elem_json['views'] = elem.find('div', class_='views').get_text(strip=True) 
            elif elem.find('span', class_='video_count'):
                elem_json['views'] = elem.find('span', class_='video_count').get_text(strip=True)
            
            
            if elem.find('a',class_='video_channel'):
                elem_json['canal'] = elem.find('a',class_='video_channel').get_text(strip=True)
            pornstars = elem.find_all('a', href=re.compile("/pornstar/[A-z0-9-]+"))
            if pornstars:
                for x, value in enumerate(pornstars):
                    pornstars[x] = value.get_text(strip=True)
                elem_json['star'] = ' & '.join(pornstars)
            
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
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)

# def play(item):
    # logger.info()
    # itemlist = []
    
    # AlfaChannel.host = config.get_setting("current_host", item.chanel, default=host)
    # AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})
    
    # soup = AlfaChannel.create_soup(item.url, **kwargs)
    
    # if soup.find_all('a', href=re.compile("/pornstar/[A-z0-9-]+")):
        # pornstars = soup.find_all('a', href=re.compile("/pornstar/[A-z0-9-]+"))
        
        # for x, value in enumerate(pornstars):
            # pornstars[x] = value.get_text(strip=True)
        
        # pornstar = ' & '.join(pornstars)
        # pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        # lista = item.contentTitle.split('[/COLOR]')
        # pornstar = pornstar.replace('[/COLOR]', '')
        # pornstar = ' %s' %pornstar
        # if AlfaChannel.color_setting.get('quality', '') in item.contentTitle:
            # lista.insert (2, pornstar)
        # else:
            # lista.insert (1, pornstar)
        # item.contentTitle = '[/COLOR]'.join(lista)



    # if "6xtube" in item.url or "blendporn" in item.url:
        # matches = soup.find('div', id='player-container')
        # item.url = matches.iframe['src']
    # itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # return itemlist


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
