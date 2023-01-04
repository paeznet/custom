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
             'channel': 'pornkinox', 
             'host': config.get_setting("current_host", 'pornkinox', default=''), 
             'host_alt': ["https://pornkinox.to/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host))
    # itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/most-popular/?sort_by=video_viewed_month&from=01"))
    # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/top-rated/1/?sort_by=rating_month&from=01"))
    # itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "/most-commented/1/?sort_by=most_commented_month&from=01"))
    # itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/models/?sort_by=avg_videos_popularity&from=01"))
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/sites/?sort_by=avg_videos_popularity&from=01"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/?sort_by=avg_videos_popularity&from=01"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%s/?s=%s" % (host,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# <li class="cat-item cat-item-16"><a href="https://pornkinox.to/amateur/" data-wpel-link="internal">Amateur Porno</a>
# </li>

def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('li', class_='cat-item')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text
        thumbnail = ""
        # cantidad = elem.find('div', class_='videos')
        # if cantidad:
            # title = "%s (%s)" % (title,cantidad.text.strip())
        # url = urlparse.urljoin(item.url,url)
        # thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    # next_page = soup.find('li', class_='item-pagin is_last')
    # if next_page:
        # next_page = next_page.a['data-parameters'].replace(":", "=").split(";").replace("+from_albums", "")
        # next_page = "?%s&%s" % (next_page[0], next_page[1])
        # next_page = urlparse.urljoin(item.url,next_page)
        # itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    soup = create_soup(item.url)
    matches = soup.find_all('article', class_=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-original']
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


# def findvideos(item):
    # logger.info()
    # itemlist = []
    # itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # return itemlist

# https://pornkinox.to/oma-die-alte-dildo-verkaeuferin/
# https://www.keeplinks.org/p28/629f4c0bc39bb

# https://filejoker.net/llq33hwpnsis/Oma_Die_alte_Dildo_Verkauferin.mp4    
# http://ddl.to/d/2aMJJ               <<<< POST
# https://tubeload.co/f/qxsehnrv795r    <<<<< REsolver

# <article class="entry clr">
# <div class="entry_table">
# <div class="entry_left">
# <a href="https://lp.mydirtyhobby.com/2/?video=2&amp;lang=de&amp;ats=eyJhIjoxOTc4NzcsImMiOjU4NjIzMDg1LCJuIjoyMSwicyI6MjQxLCJlIjo5NTQxLCJwIjoyfQ==" target="_blank" rel="nofollow external noopener" data-wpel-link="external">
# <img src="https:///pornkinox.to/wp-content/themes/pkinox/images/porn-stream.png" class=“favicon“>
# <span>Mydirtyhobby</span>
# </a>
# <a href="https://filecrypt.cc/Container/C21D0B1ABE.html" target="_blank" data-wpel-link="external" rel="nofollow external noopener">
# <img src="https:///pornkinox.to/wp-content/themes/pkinox/images/mixdrop.png" class="favicon">
# <span>mixdrop stream</span>
# </a>
# <a href="https://k2s.cc/file/c4fbba4d8426a/Boobs_Deluxe.mp4" target="_blank" data-wpel-link="external" rel="nofollow external noopener">
# <img src="https://www.google.com/s2/favicons?domain=k2s.cc" class="favicon">
# <span>k2s stream</span>
# </a>
# </div>
# </article>

# http://filecrypt.cc/Link/fDfx4cJ7GHcK6wLJtMz-SSyHGLVuEKkCgIUikt8zv3GjAdYkoObo23OUPrh9z6lvD1etBeHqVwejLceut7FEsEuyheEUUs09Z9fkrJh8jf--j0Up7TI7B7BDpuaGfEJe.html
# <button onclick="openLink('fDfx4cJ7GHcK6wLJtMz-SSyHGLVuEKkCgIUikt8zv3GjAdYkoObo23OUPrh9z6lvD1etBeHqVwejLceut7FEsEuyheEUUs09Z9fkrJh8jf--j0Up7TI7B7BDpuaGfEJe', this, true)" 

def findvideos(item):
    logger.info()
    itemlist = []
    video_url = []
    soup = create_soup(item.url)
    matches = soup.find('article', class_='entry clr').find_all('a')
    for elem in matches:
        url = elem['href']
        if "mydirtyhobby" in url:
            continue
        if not url in video_url:
            video_url.append(url)
            logger.debug(video_url)
        # title = elem.text.strip()
    for url in video_url:
        # if "filecrypt" in url:
            # data = httptools.downloadpage(url).data
            # link = scrapertools.find_single_match(data, "openLink\('([^']+)")
            # link = "http://filecrypt.cc/Link/%s.html" %link
            # data = httptools.downloadpage(link, headers={'Referer': url}).data
            # logger.debug(data)
        if "keeplinks" in url:
            headers = {'Cookie': 'flag[{0}]=1'.format(url.split('/')[-1])}
            data = httptools.downloadpage(url, headers=headers).data
            soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
            matches = soup.find('div', class_='black-box').find_all('a')
            for elem in matches:
                url = elem['href']
                logger.debug(url)
                if not "filejoker" in url:
                    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
        else:
            itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
