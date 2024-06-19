# -*- coding: utf-8 -*-
# -*- Channel Cheems -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from platformcode import config, logger
from core import scrapertools

from core.item import Item
from core import servertools, channeltools
from core import httptools
from bs4 import BeautifulSoup
from core.jsontools import json

# https://cheemsporn.com/  https://cheemsporno.com/
# https://cheemsporno.com/api/posts?perPage=36&orderBy=views&order=desc&page=1
# https://cheemsporno.com/api/posts?page=1&perPage=36&orderBy=date&order=desc latest
# https://cheemsporno.com/_next/data/szZ1j-vl4ApRKhifI4UL6/es/tags.json
# https://cheemsporno.com/api/tags?page=1&perPage=36&orderBy=name&order=asc
# https://cheemsporno.com/_next/data/szZ1j-vl4ApRKhifI4UL6/es/producers.json
# https://cheemsporno.com/api/producers?perPage=36&orderBy=views&order=asc&page=1
# https://cheemsporno.com/_next/data/szZ1j-vl4ApRKhifI4UL6/es/actors.json
# https://cheemsporno.com/api/actors?&perPage=36&orderBy=views&order=desc&page=1
 # "/posts/videos/").concat(a.slug)
# "postsNumber": 5093
canonical = {
             'channel': 'cheems', 
             'host': config.get_setting("current_host", 'cheems', default=''), 
             'host_alt': ["https://cheemsporno.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

api = "%sapi/%s?perPage=36&orderBy=%s&order=desc&page=1"
# url = "https://cheemsporno.com/api/posts/4bca4393-6703-44b9-a3e2-823d36543e00/post-views"
# referer="https://cheemsporno.com/es/posts/videos/hot-guys-fuck-naudi-nala-fucks-and-sucks-a-fat-nut-out-of-kolby-gigante-naudi-nala"
def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=api %(host, "posts", "date") ))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=api %(host, "posts", "views") ))
    itemlist.append(Item(channel=item.channel, title="Pornstar" , action="lista", url=api %(host, "actors", "views") ))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="lista", url=api %(host, "producers", "views") ))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/_next/data/szZ1j-vl4ApRKhifI4UL6/es/tags.json"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch?type=videos&sort=recent&q=%s" % (host,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(item.url).json
    if "Canal" in item.title:
        data_json = data['providers']
        id = 'providers'
    elif "Categorias" in item.title:
        data_json = data['categories']
        id = 'categories'
    else:
        data_json = data['performers']
        id = 'performers'
    
    for elem in data_json:
        if elem['count'] == 0:
            continue
        name = elem['name']
        handle = elem['handle']
        count = elem['count']
        url = "%svideos?%s=%s&page=1" %(host,id,handle)
        title = "%s (%s)" %(name,count)
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             thumbnail=thumbnail , plot=plot) )
    
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


            # color_setting = self.color_setting
            # color_default = 'white'
            # text = color_setting.get('movie', color_default)
            # stime = color_setting.get('year', color_default)
            # quality = color_setting.get('quality', color_default)
            # language = color_setting.get('cast', color_default)
            # server = color_setting.get('server', color_default)
            # canal = color_setting.get('tvshow', color_default)
            # views = color_setting.get('rating_3', color_default)
            # library = color_setting.get('library', color_default)
            # page = color_setting.get('update', color_default)
            # star = color_setting.get('rating_3', color_default)
            # error = 'red'


# from platformcode import unify
# UNIFY_PRESET = config.get_setting("preset_style", default="Inicial")
# logger.debug(unify.colors_file[UNIFY_PRESET])

color = {'movie': 'white', 'tvshow': 'salmon', 'year': 'cyan', 'rating_1': 'red', 'rating_2': 'orange',
         'rating_3': 'gold', 'quality': 'deepskyblue', 'cast': 'yellow', 'lat': 'limegreen', 'vose': 'firebrick',
         'vos': 'firebrick', 'vo': 'firebrick', 'server': 'orange', 'library': 'yellow', 'update': 'limegreen', 'no_update': 'red'}
# ['[COLOR cyan]07:54', ' [COLOR white]Teens Love Black Cocks - Mia Khalifa Deepthroat', '']
# [COLOR gold]Mia Khalifa[/COLOR]
# '[COLOR cyan]14:55[/COLOR] [COLOR cyan]Marta Villalobos[/COLOR] [COLOR salmon][Putalocura][/COLOR] Wild threesome with the Madrid girl - Marta Villalobos'


def lista(item):
    logger.info()
    itemlist = []
    data_json = httptools.downloadpage(item.url).json
    # data_json = scrapertools.find_single_match(data, "window.__INITIAL_DATA__ = (.*?);")
    # data_json = json.loads(data_json)
    for elem in data_json['posts']:  # data_json['videos']   data_json['pagination']   data_json['filters']['performers']   data_json['filters']['providers']   data_json['filters']['categories']
        canal = ""
        id = elem['post']['id']
        title = elem['post']['title']
        slug = elem['post']['slug']
        thumbnail = elem['post']['meta'][1]['value']
        segundos = elem['post']['meta'][0]['value'].split(".")[0]
        if elem['post']['producer']:
            canal = elem['post']['producer']['name']
            canal = "[COLOR %s][%s][/COLOR]" % (color.get('tvshow',''),canal)
        plot = elem['post']['description']
        
        
        segundos = int(segundos)
        horas=int(segundos/3600)
        segundos -=horas*3600
        minutos =int(segundos/60)
        segundos-=minutos*60
        if segundos < 10:
            segundos = "0%s" %segundos
        if minutos < 10:
            minutos = "0%s" %minutos
        if horas == 00:
            duration = "%s:%s" % (minutos,segundos)
        else:
            duration = "%s:%s:%s" % (horas,minutos,segundos)
        time = "[COLOR %s]%s[/COLOR]" %(color.get('year',''),duration)
        
        if canal:
            title = "%s %s %s" %(time, canal, title)
        else:
            title = "%s %s" %(time, title)

        url = "%sposts/videos/%s" %(host, slug)
        
        # plot = pornstar
        # action = "play"
        # if logger.info() == False:
            # action = "findvideos"        
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    postsNumber = data_json['postsNumber']
    lastpage = postsNumber/36
    if lastpage - int(lastpage) > 0:
        lastpage = int(lastpage) + 1
    page = int(scrapertools.find_single_match(item.url, 'page=(\d+)'))
    if page < lastpage:
        title="[COLOR blue]Página %s de %s[/COLOR]" %(page,lastpage)
        page += 1
        next_page = re.sub(r"&page=\d+", "&page={0}".format(page), item.url)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=next_page) )
    return itemlist
# ['[COLOR cyan]07:54', ' [COLOR white]Teens Love Black Cocks - Mia Khalifa Deepthroat', '']
# [COLOR gold]Mia Khalifa[/COLOR]
# '[COLOR cyan]14:55[/COLOR] [COLOR cyan]Marta Villalobos[/COLOR] [COLOR salmon][Putalocura][/COLOR] Wild threesome with the Madrid girl - Marta Villalobos'
def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    pornstars = soup.find_all('a', href=re.compile("/actors/[A-z0-9-]+"))
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR %s]%s[/COLOR]" % (color.get('rating_3',''),pornstar)
    # lista = item.contentTitle.split()
    lista = item.contentTitle.split('[/COLOR]')
    pornstar = pornstar.replace('[/COLOR]', '')
    logger.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    logger.debug(lista)
    if color.get('tvshow','') in item.title:
        lista.insert (2, pornstar)
    else:
        lista.insert (1, pornstar)
    # item.contentTitle = ' '.join(lista)    
    item.contentTitle = '[/COLOR]'.join(lista)
    
    
    patron = '\{"title":"([^"]+)"."url":"([^"]+)","type":'
    matches = scrapertools.find_multiple_matches(data, patron)
    copias=[]
    for serv, url in matches:
        marca = url.split("/")[-1].replace("embed-", "")
        if not marca in copias: 
            copias.append(marca)
            logger.debug(url)
            itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    logger.debug(copias)
    return itemlist


