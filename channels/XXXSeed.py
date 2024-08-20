# -*- coding: utf-8 -*-
# -*- Channel XXXSeed -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

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
from core import servertools
from core import httptools
from bs4 import BeautifulSoup
from core import jsontools as json

forced_proxy_opt = 'ProxySSL'

#https://pornseed.net/   https://xxxseed.com/

canonical = {
             'channel': 'XXXSeed', 
             'host': config.get_setting("current_host", 'XXXSeed', default=''), 
             'host_alt': ["https://pornseed.net/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
api = "https://cdn.f2share.com/"

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "search?sortBy=createdAt&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistos" , action="list_all", url=host + "search?sortBy=views&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=host + "search?sortBy=liked&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=host + "search?sortBy=duration&page=1"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "collections", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="categorias", url=host + "pornstars?page=1", extra="PornStar"))
    # itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "tags/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch/%s/?sortBy=createdAt&page=1" % (host,texto)
    try:
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


{'id': 'abella-danger', 
 'name': 'Abella Danger', 
 'description': '<p>Abella Danger has one of the most famous asses in the porn biz, but despite her iconic, juicy booty, this curvy brunette is just as notable for her beautiful face and unbelievably dirty mouth. Her superior posterior is only one of the many reasons why Abella has shot to the top of the adult film industry since her debut in 2014. Abella says she\'s on the pursuit of pleasure, and this busty babe has the brains not just to mix pleasure with business, but to turn it into an empire. Abella is ready to assume the throne, and all her subjects are happy to bow down. This stunner has quickly gained thousands of fans who can\'t tear their eyes away from Abella\'s always-intense scenes and insist she\'s one of the hottest young performers in the porn biz today. The industry agrees: in 2016, Abella won both the AVN and XBIZ awards for Best New Starlet. She has already demonstrated her talent with her genre-spanning work, but she says her goal is to keep growing and improving, and it\'s clear there\'s no stopping this talented performer who\'s poised to make the industry her own: Abella says, "I may have fallen into porn by accident, but it was meant for me."</p>', 
 'data': None, 'views': 10940, 
 'image': 'dev-movie-bucket/static/bUcojujBme_IMG.jpg', 'gallery': []}


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    data = soup.find('script', id='__NEXT_DATA__').string
    JSONData = json.load(data)['props']['pageProps']['data']
    
    if "PornStar" in item.extra:
        total = JSONData['total']
        JSONData = JSONData['data']
    
    for elem in JSONData:
        if "PornStar" in item.extra:
            url = "%spornstars/%s" %(host, elem['id'])
            title = elem['name']
            url += "?sortBy=createdAt&page=1"
        else:
            url = "%ssearch?collection=%s" %(host, elem['id'])
            title = elem['title']
            url += "&sortBy=createdAt&page=1"
        thumbnail = ""
        if elem.get('image', ''):
            thumbnail = "%s%s" %(api, elem['image'])
        plot = ""
        itemlist.append(Item(channel=item.channel, action="list_all", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    if "PornStar" in item.extra:
        page = int(scrapertools.find_single_match(item.url, 'page=([0-9]+)'))
        next = page * 36
        if total > next:
            next_page = page + 1
            next_page = re.sub(r"&page=\d+", "&page={0}".format(next_page), item.url)
            itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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


def list_all(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    data = soup.find('script', id='__NEXT_DATA__').string
    if "pornstars" in item.url:
        JSONData = json.load(data)['props']['pageProps']
        total = JSONData['videoTotal']
        # JSONData = JSONData['pornstar']['movies']
        JSONData = JSONData['videos']
    else:
        JSONData = json.load(data)['props']['pageProps']['data']
        total = JSONData['total']
        JSONData = JSONData['data']
    
    for elem in JSONData:
        url = "%svideo/%s" %(host, elem['sku'])
        title = elem['title']
        thumbnail = "%s%s" %(api, elem['image'])
        video = "%s%s" %(api, elem['encodeVideo'])
        
        segundos = elem['duration']
        horas=int(segundos/3600)
        segundos-=horas*3600
        minutos=int(segundos/60)
        segundos-=minutos*60
        if segundos < 10:
            segundos = "0%s" %segundos
        if minutos < 10:
            minutos = "0%s" %minutos
        if horas == 00:
            time = "%s:%s" % (minutos,segundos)
        else:
            time = "%s:%s:%s" % (horas,minutos,segundos)
        
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        thumbnail += "|Referer=%s" % host #"|verifypeer=false"
        plot = elem['description']
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    
    page = int(scrapertools.find_single_match(item.url, '&page=([0-9]+)'))
    next = page * 36
    if total > next:
        next_page = page + 1
        next_page = re.sub(r"&page=\d+", "&page={0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="list_all", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

from platformcode import unify
UNIFY_PRESET = config.get_setting("preset_style", default="Inicial")
color = unify.colors_file[UNIFY_PRESET]
# color = {'movie': 'white', 'tvshow': 'salmon', 'year': 'cyan', 'rating_1': 'red', 'rating_2': 'orange',
         # 'rating_3': 'gold', 'quality': 'deepskyblue', 'cast': 'yellow', 'lat': 'limegreen', 'vose': 'firebrick',
         # 'vos': 'firebrick', 'vo': 'firebrick', 'server': 'orange', 'library': 'yellow', 'update': 'limegreen', 'no_update': 'red'}


def play(item):
    logger.info()
    itemlist = []
    
    soup = create_soup(item.url)
    data = soup.find('script', id='__NEXT_DATA__').string
    JSONData = json.load(data)['props']['pageProps']['video']
    
    if JSONData['actors']:
        pornstars = []
        for elem in JSONData['actors']:
            pornstars.append(elem['name']) 
            
        pornstar = ' & '.join(pornstars)
        pornstar = "[COLOR %s]%s[/COLOR]" %(color.get('rating_3',''), pornstar)
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s' %pornstar
        lista.insert (1, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)
    
    video = JSONData['encodeVideo']
    video = "%s%s" %(api,video)
    data = httptools.downloadpage(video, headers={'Referer': host}).data
    if isinstance(data, bytes):
        data = data.decode("utf8")
    
    patron = 'RESOLUTION=\d+x(\d+).*?'
    patron += '(.*?.m3u8)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for quality,url in matches:
        url = url.replace("iframes", "index")
        url = urlparse.urljoin(video,url)
        itemlist.append(['[XXXSeed] .m3u8 %sp' %quality, url])
    itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return itemlist

