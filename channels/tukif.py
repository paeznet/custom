# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup
from core import jsontools as json

canonical = {
             'channel': 'tukif', 
             'host': config.get_setting("current_host", 'tukif', default=''), 
             'host_alt': ["https://tukif.porn/"], 
             'host_black_list': ["https://tukif.com/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
hosta = '%sposts/load_more_posts/' %host
# https://tukif.porn/posts/load_more_posts?main_category_id=1&type=post&name=multifilter_videos&filters%5Bfilter_type%5D=date&filters%5Bfilter_period%5D=month&filters%5Bfilter_quality%5D%5B%5D=270&filters%5Bfilter_duration%5D%5B%5D=45&filters%5Bfilter_duration%5D%5B%5D=26&filters%5Bfilter_duration%5D%5B%5D=15&filters%5Bfilter_duration%5D%5B%5D=14&adblock_enabled=&offset=0
post = "main_category_id=%s&type=%s&name=%s&filters[filter_type]=%s&filters[filter_period]=%s&filters[filter_quality][]=270&filters[filter_duration][]=14&adblock_enabled=1&current_page_offset=0&offset=0"
                                                                                                                                                                        # current_page_offset	"0"                
def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Pro" , action="submenu", id="1" ))
    itemlist.append(Item(channel=item.channel, title="Amateur" , action="submenu", id="4" ))
    itemlist.append(Item(channel=item.channel, title="Gay" , action="submenu", id="2" ))
    itemlist.append(Item(channel=item.channel, title="Trans" , action="submenu", id="3" ))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    if item.id == "1": url= "%svideos/" % host
    if item.id == "2": url= "%sgay/videos/" % host
    if item.id == "3": url= "%stransexuel/videos/" % host
    if item.id == "4": url= "%samateur/videos/" % host

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=hosta, post= post % (item.id, "post", "multifilter_videos","date", "month")))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=hosta, post= post % (item.id, "post", "multifilter_videos","views","month")))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=hosta, post= post % (item.id, "post", "multifilter_videos","rating","month")))
    itemlist.append(Item(channel=item.channel, title="Mas metraje" , action="lista", url=hosta, post= post % (item.id, "post", "multifilter_videos","duration","month")))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=hosta, post= post % (item.id, "post", "multifilter_videos","comments","month")))
    if item.id == "1":
        stud= 'main_category_id=1&type=studio&name=top_studios&filters[filter_type]=popularity&adblock_enabled=1&starting_letter=&offset=0&current_page_offset=0'
        star= 'main_category_id=1&type=pornstar&name=top_pornstars&filters[filter_type]=popularity&adblock_enabled=1&starting_letter=&offset=0'
        itemlist.append(Item(channel=item.channel, title="PornStar" , action="catalogo", url=host + "pornstars/load_more_pornstars", post= star))
        itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "studios/load_more_studios", post= stud))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=url, post= post % (item.id, "post", "multifilter_videos","date", "")))

    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host + "posts/load_more_search_posts", id=item.id))
    return itemlist


def search(item, texto):
    logger.info()
    itemlist = []
    texto = texto.replace(" ", "+")
    item.post = post % (item.id, "search_post", "search_post","date", "")
    item.post += "&search=%s" %texto
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def catalogo(item):
    logger.info()
    itemlist = []
    headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    data = httptools.downloadpage(item.url, headers=headers, post=item.post).json
    data = data['data']
    soup = BeautifulSoup(data['content'], "html5lib", from_encoding="utf-8")
    matches = soup.find_all('div', class_='showcase_item_wrapper')
    for elem in matches:
        if "studios" in item.url:
            name = "studio_related_videos"
        else:
            name = "pornstar_related_videos"
        num = elem['id'].replace("_", "")
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        cantidad = elem.find('div', class_='showcase_views',).text.strip()
        title = "%s (%s)" % (title,cantidad)
        post = "main_category_id=%s&type=post&name=%s&filters[filter_type]=date&filters[filter_period]=&filters[filter_quality][]=270&adblock_enabled=1&content_id=%s&offset=0" %(item.id,name,num)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=hosta, post = post,
                                 thumbnail=thumbnail, fanart=thumbnail, contentTitle=title ))
    count= data['total']
    current_page = scrapertools.find_single_match(item.post, ".*?&offset=(\d+)")
    current_page = int(current_page)
    if current_page <= int(count) and (int(count) - current_page) > 30:
        current_page += 30
        next_page = re.sub(r"&offset=\d+", "&offset={0}".format(current_page), item.post)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", post=next_page) )
    return itemlist


def categorias(item):
    import base64
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('div', class_='sidebar_category_list_wrapper')
    matches = soup.find_all('span', class_='sidebar_section_item obfs')
    for elem in matches:
        url = elem['data-obfs']
        url = base64.b64decode(url).decode('utf-8') #.replace("%2F", "/")
        url = urlparse.unquote(url)
        title = elem['title']
        if "/channels/" in url:
            url = url.replace("/channels/", "").split("/")
            url = "&multifilter[%s]=%s" %(url[0],url[1])
            post = re.sub(r"&adblock_enabled=1", "&adblock_enabled=1{0}".format(url), item.post)
            thumbnail = ""
            plot = ""
            itemlist.append(Item(channel=item.channel, action="lista", title=title, url=hosta, post=post,
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


def lista(item):
    logger.info()
    itemlist = []
    headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    data = httptools.downloadpage(item.url, headers=headers, post=item.post, canonical=canonical).json
    data = data['data']
    soup = BeautifulSoup(data['content'], "html5lib", from_encoding="utf-8")
    matches = soup.find_all('section')
    for elem in matches:
        logger.debug(elem)
        url = elem.a['href']
        title = elem.a.text.strip()
        thumbnail = elem.find('img', class_='thumb_preview')['data-src']
        time = elem.find('div', class_='bubble_duration').text.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    count= data['total']
    quantity = data['quantity']
    pages = data['total_pages']
    current_page = scrapertools.find_single_match(item.post, ".*?&offset=(\d+)")
    current_page = int(current_page)
    if current_page <= int(count) and (int(count) - current_page) > int(quantity):
        current_page += int(quantity)
        next_page = re.sub(r"&offset=\d+", "&offset={0}".format(current_page), item.post)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", post=next_page, url= item.url) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    url = scrapertools.find_single_match(data, '<iframe src="([^"]+)"')
    data = httptools.downloadpage(url).data
    source= scrapertools.find_single_match(data, '("srcSet":.*?])')
    source = "{%s}" %source
    JSONData = json.load(source)
    for elem in JSONData['sources']:
        if "video/mp4" in elem['type']:
            url = elem['src']
            quality = elem['label']
            itemlist.append(Item(channel=item.channel, action="play", title=quality, url=url) )
    return itemlist[::-1]


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    url = scrapertools.find_single_match(data, '<iframe src="([^"]+)"')
    data = httptools.downloadpage(url).data
    source= scrapertools.find_single_match(data, '("srcSet":.*?])')
    source = "{%s}" %source
    JSONData = json.load(source)
    for elem in JSONData['srcSet']:
        if "video/mp4" in elem['type']:
            url = elem['src']
            quality = elem['label']
            itemlist.append(['[tukif] %s .mp4' %quality, url])
    return itemlist[::-1]
