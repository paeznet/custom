# -*- coding: utf-8 -*-
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
from core import servertools
from core import httptools
from bs4 import BeautifulSoup
from core import jsontools as json


canonical = {
             'channel': 'yaske', 
             'host': config.get_setting("current_host", 'yaske', default=''), 
             'host_alt': ["https://yaske.ru/"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s*rel="?stylesheet"?'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]



#Nuevos             https://yaske.ru/api/v1/channel/2?returnContentOnly=true&restriction=&order=created_at:desc&perPage=50&query=&page=1
#Mas visto          https://yaske.ru/api/v1/channel/2?returnContentOnly=true&restriction=&order=popularity:desc&perPage=50&query=&page=1
#Mejor valorado     https://yaske.ru/api/v1/channel/2?returnContentOnly=true&restriction=&order=rating:desc&perPage=50&query=&page=1
#Mas ingresos       https://yaske.ru/api/v1/channel/2?returnContentOnly=true&restriction=&order=revenue:desc&perPage=50&query=&page=1
#Mayor presupuesto  https://yaske.ru/api/v1/channel/2?returnContentOnly=true&restriction=&order=budget:desc&perPage=50&query=&page=1
#                   https://yaske.ru/api/v1/channel/3?returnContentOnly=true&restriction=&order=created_at:desc&perPage=50&query=&page=1
                                                  # 2 pelis
                                                  # 3 series
                                                  # 30 estrenos series
                                                  # 31 estrenos pelis
                                                    
def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Findvideos" , action="findvideos", url=host + "watch/207914"))
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "movies?order=created_at%3Adesc"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "?sort_by=video_viewed_month&from=01"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "?sort_by=rating_month&from=01"))
    itemlist.append(Item(channel=item.channel, title="Favoritos" , action="lista", url=host + "?sort_by=most_favourited&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "?sort_by=most_commented&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "?sort_by=duration&from=1"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "models/?sort_by=total_videos&from=01"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "sites/?sort_by=total_videos&from=01"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/?sort_by=title"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ssearch/%s/?sort_by=post_date&from_videos=01" % (host,texto)
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
    soup = create_soup(item.url)
    matches = soup.find_all('a', class_='item')
    for elem in matches:
        url = elem['href']
        title = elem['title']
        if elem.find('span', class_='no-thumb'):
            thumbnail = ""
        else:
            thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-src']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        cantidad = elem.find('div', class_='videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        # url = urlparse.urljoin(item.url,url)
        # thumbnail = urlparse.urljoin(item.url,thumbnail)
        url += "?sort_by=post_date&from=01"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='next')
    if next_page and next_page.find('a'):
        next_page = next_page.a['data-parameters'].split(":")[-1]
        if "from_videos" in item.url:
            next_page = re.sub(r"&from_videos=\d+", "&from_videos={0}".format(next_page), item.url)
        else:
            next_page = re.sub(r"&from=\d+", "&from={0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
        logger.debug(data)
        # data = scrapertools.find_single_match(data, "window.bootstrapData\s*=\s*(.*?);\s*</script")
        # JSONData = json.load(data)
        # logger.debug(JSONData['settings']['video']['qualities'])# ['videos'] ['downloads'] ['alternative_videos']
        # logger.debug(JSONData['loaders']['watchPage']['title']['videos'])# ['videos'] ['downloads'] ['alternative_videos']
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_=re.compile(r"^item-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-original']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        time = elem.find('div', class_='duration').text.strip()
        quality = elem.find('span', class_='is-hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='next')
    if next_page and next_page.find('a'):
        next_page = next_page.a['data-parameters'].split(":")[-1]
        if "from_videos" in item.url:
            next_page = re.sub(r"&from_videos=\d+", "&from_videos={0}".format(next_page), item.url)
        else:
            next_page = re.sub(r"&from=\d+", "&from={0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data, "window.bootstrapData\s*=\s*(.*?);\s*</script")
    JSONData = json.load(data)
    # logger.debug(JSONData['settings']['video']['qualities'])# ['videos'] ['downloads'] ['alternative_videos']
    # logger.debug(JSONData['loaders']['watchPage']['title']['videos'])# ['videos'] ['downloads'] ['alternative_videos']
    calidad = JSONData['settings']['video']['qualities']
    patron = '"uuid":"([^"]+)","name":"([^"]+)"'
    matches = scrapertools.find_multiple_matches(calidad, patron)
    for quality, name in matches:
        logger.debug(quality +" - "+ name)
    videos = JSONData['loaders']['watchPage']['title']['videos']
    downloads = JSONData['loaders']['watchPage']['title']['downloads']
    # alternative = JSONData['loaders']['watchPage']['title']['alternative_videos']
    for elem in videos:
        # logger.debug(elem['id'])
        url = elem['src']
        quality = elem['quality']
        language = elem ['language']
        domain = elem ['domain']
        url = urlparse.urljoin(item.url,url)
        video = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers["location"]
        # url = httptools.downloadpage(url).url
        logger.debug(video)
        {'id': 36388, 'name': None, 'thumbnail': None, 
         'src': '/link/vRqxp8gq0x', 'type': 'embed', 
         'quality': '5f744bff-7374-40c2-8f22-bb493823d3b9', 'title_id': 41, 
         'season_num': None, 
         'episode_num': None, 'origin': 'tmdb', 'downvotes': 0, 'upvotes': 0, 'approved': True, 'order': 0, 'created_at': '2024-07-27T03:32:50.000000Z', 'updated_at': '2024-07-27T03:32:50.000000Z', 'user_id': None, 
         'language': 'en', 'category': 'full', 'episode_id': None, 
         'hash': 'vRqxp8gq0x', 'score': None, 'model_type': 'video', 
         'domain': 'jwplayerhls.com', 'encoded_id': ''}, 
        itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


# def play(item):
    # logger.info()

    # itemlist = []
    # kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 
              # 'timeout': timeout, 'cf_assistant': False, 'canonical': {}, 'soup': False}

    # if item.server not in ['openload', 'streamcherry', 'streamango']:
        # item.server = ''

    # try:
        # new_data = AlfaChannel.create_soup(item.url, **kwargs).data
        # if "gamovideo" in item.url:
            # item.url = scrapertools.find_single_match(new_data, '<a href="([^"]+)"')
        # else:
            # new_enc_url = scrapertools.find_single_match(new_data, '<iframe\s*class=[^>]+src="([^"]+)"')

            # try:
                # item.url = AlfaChannel.create_soup(new_enc_url, follow_redirects=False, **kwargs).headers['location']
            # except:
                # if not 'jquery' in new_enc_url:
                    # item.url = new_enc_url
    # except:
        # pass

    # if not item.url:
        # return []

    # itemlist.append(item.clone())
    # itemlist = servertools.get_servers_itemlist(itemlist)

    # return itemlist
# def play(item):
    # logger.info()
    # itemlist = []
    # soup = create_soup(item.url)
    # pornstars = soup.find_all('a', href=re.compile("/models/[A-z0-9-]+/"))
    # for x , value in enumerate(pornstars):
        # pornstars[x] = value.text.strip()
    # pornstar = ' & '.join(pornstars)
    # pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    # lista = item.contentTitle.split()
    # if "HD" in item.title:
        # lista.insert (4, pornstar)
    # else:
        # lista.insert (2, pornstar)
    # item.contentTitle = ' '.join(lista)
    
    # itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # return itemlist
