# -*- coding: utf-8 -*-
# -*- Channel xKeezMovies -*-
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
             'channel': 'xkeezmovies', 
             'host': config.get_setting("current_host", 'xkeezmovies', default=''), 
             'host_alt': ["https://xkeezmovies.com/"], 
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



# post_content   https://xkeezmovies.com/nurumassage-river-lynn-the-fucket-list-pizza-with-a-side-of-nuru-07-14-2025/
# rich-content   https://xkeezmovies.com/bigtitsroundasses-red-eviee-piping-hot-sweaty-tits-01-18-2025/
# <div class='video'><iframe src= (hqq.to, https://player.xkeezmovies.com/) NETU   https://xkeezmovies.com/7803-daria-czechcasting/
# # <div id='player-torotube'><iframe src=   https://xkeezmovies.com/right-signals-sent-and-received-premium-porn/
# <video id  sourtype  https://xkeezmovies.com/i-do-need-a-hand-here-sis-premium-porn/



finds = {'find': {'find_all': [{'tag': ['div'], 'class': re.compile(r"^post-\d+")}]},     #'id': re.compile(r"^browse_\d+")}]},
         'categories': {'find_all': [{'tag': ['span'], 'class': ['catlist']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+', '/page/%s'], ['&page=\d+', '&page=%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pag-nav']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': 'page/(\d+)'}])]), 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['div'], 'class': ['section-box']}]), 
                             ('find_all', [{'tagOR': ['a'], 'href': True, 'rel': 'noreferrer'},
                                           {'tagOR': ['div'], 'id': ['player-torotube']},
                                           {'tagOR': ['div'], 'class': ['video']},
                                           {'tag': ['a'], 'class': [re.compile(r"^button\d+")]}])]),
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
                            # 'section_cantidad': dict([('find', [{'tag': ['div'], 'class': ['thumb-item']}]),
                                                      # ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(\d+)'}])])
                           },
         'controls': {'url_base64': False, 'cnt_tot': 39, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "page/1/?orderby=date"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistos" , action="list_all", url=host + "page/1/?orderby=views"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=host + "page/1/?orderby=likes"))
    itemlist.append(Item(channel=item.channel, title="Random" , action="list_all", url=host + "page/1/?orderby=rand"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "studios/", extra="Canal"))
    # itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "pornstar", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "category/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:category|pornstars)\/[^$]+$)', r'\1page/1/?orderby=date']]
    
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
    return AlfaChannel.section(item, finds=findS, **kwargs)
    # return AlfaChannel.section(item, **kwargs)
    # return AlfaChannel.section(item, matches_post=section_matches, **kwargs)


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
    return matches


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    findS['controls']['action'] = 'findvideos'
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=False, generictools=True, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    
    soup = AHkwargs.get('soup', {})
    if soup.find('div', id='details').find('div', class_='entry-content').find_all('a', rel="tag"):
        pornstars = soup.find('div', id='details').find('div', class_='entry-content').find_all('a', rel="tag")
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        # lista = item.contentTitle.split('[/COLOR]')
        # pornstar = pornstar.replace('[/COLOR]', '')
        # pornstar = ' %s' %pornstar
        # if AlfaChannel.color_setting.get('quality', '') in item.contentTitle:
            # lista.insert (2, pornstar)
        # else:
            # lista.insert (1, pornstar)
        # item.contentTitle = '[/COLOR]'.join(lista)
        item.plot = pornstar
    
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            if elem.get('href',''):
                url = elem['href']
            else:
                url = elem.iframe['src']
                # if 'hqq' in url or 'player.xkeezmovies' in url:
                    # from platformcode import platformtools
                    # platformtools.dialog_ok("Server no soportado:", "%s" %url)
                    # return
            if "player.xkeezmovies.com" in url:
                url= url.replace("player.xkeezmovies.com", "hqq.to")
            logger.debug(url)
            elem_json['url'] = url
            elem_json['server'] = ''
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
    
    # item.url = "%sbuscar/?q=%s&sort_by=video_viewed&from_videos=1" % (host, texto.replace(" ", "+"))
    item.url = "%spage/1/?s=%s&orderby=date" % (host, texto.replace(" ", "+"))
    
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
