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

canonical = {
             'channel': 'udvl', 
             'host': config.get_setting("current_host", 'udvl', default=''), 
             'host_alt': ["https://udvl.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/latest-updates/1/"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/most-popular/1/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/top-rated/1/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search/?q=%s" % (host,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# <div class="preview">
		            # <div class="preview-ins preview-cat-ins">
		                # <a href="https://udvl.com/categories/amateur/">
		                    # <div class="preview-img">
		                       	# <img class="thumb" src="//udvl.b-cdn.net/contents/categories/1/s1_1.jpg" alt="Amateur">
		                        # <div class="preview-icon">
		                            # <div class="icon"><i class="fa fa-bookmark"></i></div>
		                        # </div>
		                        # <div class="dur"><i class="fa fa-youtube-play"></i> 9445 videos</div>
		                    # </div>
		                    # <div class="name">Amateur</div>
		                # </a>
		            # </div>
		        # </div>

def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='preview')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('div', class_='name').text.strip()
        thumbnail = elem.img['src']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        cantidad = elem.find('div', class_='dur')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        # url = urlparse.urljoin(item.url,url)
        # thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    return itemlist

def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


# <div class="preview">
                # <div class="preview-ins">
                   # <a href="https://udvl.com/videos/41856/perv-nana-charming-milf-and-stepsister-joined-together-to-give-stepson-an-ultimate-sexual-experience/">
                        # <div class="preview-img img_thumb" data-src="//udvl.b-cdn.net/contents/videos_screenshots/41000/41856/320x180/" data-cnt="5">
                            # <img class="thumb " src="//udvl.b-cdn.net/contents/videos_screenshots/41000/41856/320x180/1.jpg" data-webp="//udvl.b-cdn.net/contents/videos_screenshots/41000/41856/336x189/1.jpg" alt="Perv Nana - Charming Milf And Stepsister Joined Together To Give Stepson An Ultimate Sexual Experience" data-cnt="5" width="320" height="180">
                            # <div class="preview-icon">
                                # <div class="icon"><i class="fa fa-caret-right"></i></div>
                            # </div>
                            # <div class="dur"><i class="fa fa-clock-o"></i> 20:37</div>
                        # </div>
                        # <div class="preview-bottom">
                            # <ul>
                            									                                # <li class="preview-likes"><i class="fa fa-thumbs-up"></i> 86% <span>(224 votes)</span></li>
                                # <li class="preview-views"><i class="fa fa-eye"></i> 99 392 <span>views</span></li>
                            # </ul>
                        # </div>
                        # <div class="name">Perv Nana - Charming Milf And Stepsister Joined Together To Give Stepson An Ultimate Sexual Experience</div>
                    # </a>
                # </div>
            # </div>
# <li class="next"><a href="/latest-updates/3/" data-container-id="list_videos_latest_videos_list_pagination" data-block-id="list_videos_latest_videos_list" data-parameters="sort_by:post_date;from:3">Next</a></li>

def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='preview')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('div', class_='name').text.strip()
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-original']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        time = elem.find('div', class_='dur').text.strip()
        quality = elem.find('span', class_='label hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('li', class_='next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('source', type='video/mp4')['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('source', type='video/mp4')['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
