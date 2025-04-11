# -*- coding: utf-8 -*-
# -*- Channel PornVase -*-
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
             'channel': 'zigtube', 
             'host': config.get_setting("current_host", 'zigtube', default=''), 
             'host_alt': ["https://www.zigtube.com/"], 
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

finds = {'find': {'find_all': [{'tag': ['li'], 'class': ['video']}]},     #'id': re.compile(r"^browse_\d+")}]},
         'categories': {'find_all': [{'tag': ['li'], 'class': ['category']}]}, 
         # 'categories': dict([('find', [{'tag': ['div'], 'class': ['videos-list']}]),
                             # ('find_all', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         # 'next_page': dict([('find', [{'tag': ['li'], 'class': ['next']}, {'tag': ['a'], '@ARG': 'href'}])]),
         # 'next_page': dict([('find', [{'tag': ['a'], 'class': ['current']}]),
                            # ('find_all', [{'tag': ['a'], 'class': ['current'], 
                                          # '@POS': [-1], '@ARG': 'href'}])]), 
         # 'next_page': dict([('find', [{'tag': ['div'], 'class': ['pagination-page-bas']}, {'tag': ['span']}]),
                            # ('find_next_sibling', [{'tag': ['a'], '@ARG': 'href'}])]), 
         # 'next_page': dict([('find', [{'tag': ['a'], 'class': 'tm_pag_nav_next', '@ARG': 'href'}])]), 
         # 'next_page': {'find': [{'tag': ['a'], 'string': re.compile('(?i)(?:more|next)'), '@ARG': 'href'}]}, #### COGE blog que tiene more
         # 'next_page': dict([('find', [{'tag': ['div', 'ul'], 'class': ['pagination']}]), 
                            # ('find_all', [{'tag': ['a'], 'string': re.compile('(?i)(?:more|next)'), '@POS': [-1], '@ARG': 'href'}])]),
         'next_page': {},
         'next_page_rgx': [['\/\d+', '/%s'], ['&page=\d+', '&page=%s']], 
         'last_page': dict([('find', [{'tag': ['ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'href', '@TEXT': '(?:/|=)(\d+)'}])]), 
         # 'last_page': dict([('find', [{'tag': ['span'], 'class': ['navigation']}]), 
                            # ('find_all', [{'tag': ['a'], '@POS': [-1]}]),
                            # ('get_text', [{'strip': True}])]), 
         # 'last_page':  dict([('find', [{'tag': ['script'], 'string': re.compile('(?i)var objectPagination')}]), 
                             # ('get_text', [{'strip': True, '@TEXT': 'total:\s*(\d+)'}])]), 
         # 'last_page': {},
         'plot': {}, 
         # 'findvideos': dict([('find', [{'tag': ['li'], 'class': 'link-tabs-container', '@ARG': 'href'}]),
                             # ('find_all', [{'tag': ['a'], '@ARG': 'href'}])]),
         # 'findvideos': dict([('find', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}]), 
                             # ('find_all', [{'tagOR': ['a'], 'href': True, 'id': 'tracking-url'},
                                           # {'tag': ['iframe'], 'src': True}])]),
         'findvideos': {},
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
                            'section_cantidad': dict([('find', [{'tag': ['div'], 'class': ['thumb-item']}]),
                                                      ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(\d+)'}])])
                           },
         'controls': {'url_base64': False, 'cnt_tot': 40, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)

# https://www.zigtube.com/search/video/?s=big+natural+tits&o=recent&page=1
                                                        # &o=viewed&t=month&page=2
                                                        # &o=rated&t=month&page=2
                                                        # &o=longest&page=2

def mainlist(item):
    logger.info()
    itemlist = []
    # autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "videos/"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistos" , action="list_all", url=host + "videos/viewed/month/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=host + "videos/rated/month/"))
    itemlist.append(Item(channel=item.channel, title="Favoritos" , action="list_all", url=host + "videos/favorited/"))
    itemlist.append(Item(channel=item.channel, title="Mas Comentado" , action="list_all", url=host + "videos/discussed/"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=host + "videos/longest/"))
    itemlist.append(Item(channel=item.channel, title="Mas Descargas" , action="list_all", url=host + "videos/downloaded/"))
    itemlist.append(Item(channel=item.channel, title="Trending" , action="list_all", url=host + "videos/watched/"))
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "channel/top-rated", extra="Canal"))
    # itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "pornstar", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "categories/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    # autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    # logger.debug(soup)
    matches = soup.find_all('li', id=re.compile(r"^browse_\d+"))
    for elem in matches:
        # logger.debug(elem)
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['data-src']
        time = elem.find('span', class_='duration').text.strip()
        quality = elem.find('span', class_='video_quality')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (time,quality.text.strip(),title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)

        itemlist.append(Item(channel=item.channel, action='play', title=title, contentTitle = title, url=url,
                 fanart=thumbnail, thumbnail=thumbnail))
    next_page = soup.find('a', class_='tm_pag_nav_next')
    if next_page:
        next_page = next_page['href']
        next_page = AlfaChannel.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def section(item):
    logger.info()
    
    # findS = finds.copy()
    # findS['url_replace'] = [['(\/(?:categories|channels|models|pornstars)\/[^$]+$)', r'\1?sort_by=post_date&from=1']]
    
    # if item.extra == 'PornStar':
        # findS['categories'] = dict([('find', [{'tag': ['div'], 'class': 'list-models'}]), 
                                    # ('find_all', [{'tag': ['a'], 'class': 'item'}])])
    
    # if item.extra == 'Canal':
        # findS['categories'] = dict([('find', [{'tag': ['div'], 'id': 'popup-sponsors'}]), 
                                    # ('find_all', [{'tag': ['li']}])])
        # findS['profile_labels']['section_title'] = {'find': [{'tag': ['img'], '@ARG': 'alt'}]}
        # findS['last_page'] = {}
        # findS['controls']['cnt_tot'] = 12
    
    # if item.extra == 'Categorias':
        # findS['categories'] = dict([('find', [{'tag': ['div'], 'class': 'list-categories'}]), 
                                    # ('find_all', [{'tag': ['a']}])])
    # return AlfaChannel.section(item, finds=findS, **kwargs)
    return AlfaChannel.section(item, **kwargs)
    # return AlfaChannel.section(item, matches_post=section_matches, **kwargs)


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
    soup = AHkwargs.get('soup', {})
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
        
        try:
            
            elem_json['url'] = elem.get("href", '') or elem.a.get("href", '')
            elem_json['title'] = elem.a.get('data-mxptext', '') or elem.a.get('title', '') \
                                                                or (elem.img.get('alt', '') if elem.img else '') \
                                                                or elem.a.get_text(strip=True)
            if elem.img: elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                                                                     or elem.img.get('data-src', '') \
                                                                                     or elem.img.get('src', '')
            if elem.find('span', class_=['videoCount', 'videosNumber']):
                elem_json['cantidad'] = elem.find('span', class_=['videoCount', 'videosNumber']).get_text(strip=True)
            elif elem.find('div', class_='videos'):
                elem_json['cantidad'] = elem.find('div', class_='videos').get_text(strip=True)
            elif elem.find(string=re.compile(r"(?i)videos|movies")):
                elem_json['cantidad'] = elem.find(string=re.compile(r"(?i)videos|movies")).strip()
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
    
    # findS = finds.copy()
    # findS['controls']['action'] = 'findvideos'
    
    # return AlfaChannel.list_all(item, finds=findS, **kwargs)
    return AlfaChannel.list_all(item, **kwargs)
    # return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


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
            

            elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') \
                                     or elem.img.get('src', '')
            elem_json['stime'] = elem.find(class_='duration').get_text(strip=True) if elem.find(class_='duration') else ''
            # if not elem_json['stime'] and elem.find(text=lambda text: isinstance(text, self.Comment) \
                                      # and 'duration' in text):
                # elem_json['stime'] = self.do_soup(elem.find(text=lambda text: isinstance(text, self.Comment) \
                                                  # and 'duration' in text)).find(class_='duration').get_text(strip=True)
            if not elem_json['stime'] and elem.find(string=re.compile('^([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$')):
                elem_json['stime'] = elem.find(string=re.compile('^([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$'))
            if elem.find('span', class_=['hd-thumbnail', 'is-hd']):
                elem_json['quality'] = elem.find('span', class_=['hd-thumbnail', 'is-hd']).get_text(strip=True)
            if elem.find('span', class_=['hd-thumbnail', 'is-hd', 'video_quality']):
                elem_json['quality'] = elem.find('span', class_=['hd-thumbnail', 'is-hd', 'video_quality']).get_text(strip=True)
            elem_json['stime'] = elem_json['stime'].replace(elem_json['quality'], '')
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
            
            
            if elem.find('a',class_='video_channel'):
                elem_json['canal'] = elem.find('a',class_='video_channel').get_text(strip=True)
            pornstars = elem.find_all('li', class_="pstar")
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


    # return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         # verify_links=False, generictools=True, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()
    matches = []
    findS = AHkwargs.get('finds', finds)
    srv_ids = {"Doodstream": "Doodstream",
               "Streamtape": "Streamtape ",
               "StreamSB": "Streamsb",
               "VOE": "voe",
               "MIXdrop": "Mixdrop",
               "Upstream": "Upstream"}
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            elem_json['url'] = elem.get("href", "")
            elem_json['server'] = elem.get_text(strip=True).capitalize()
            if elem_json['server'] in ["Netu", "trailer"]: continue
            if elem_json['server'] in srv_ids:
                elem_json['server'] = srv_ids[elem_json['server']]
            elem_json['language'] = ''
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())

        if not elem_json.get('url', ''): continue
        matches.append(elem_json.copy())

    return matches, langs


# def play(item):
    # logger.info()
    
    # itemlist = []
    
    # soup = AHkwargs.get('soup', {})
    # soup = AlfaChannel.create_soup(item.url, **kwargs)
    
    # if soup.find_all('li', class_="starw"):
        # pornstars = soup.find_all('li', class_="starw")
        # pornstars = soup.find_all('a', href=re.compile("/models/[A-z0-9-]+/"))
        
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
    
    # itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    # return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    # item.url = "%sbuscar/?q=%s&sort_by=video_viewed&from_videos=1" % (host, texto.replace(" ", "+"))
    item.url = "%ssearch/video/?s=%s&o=recent&page=1" % (host, texto.replace(" ", "+"))
    
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
