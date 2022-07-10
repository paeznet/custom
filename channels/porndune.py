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
             'channel': 'porndune', 
             'host': config.get_setting("current_host", 'porndune', default=''), 
             'host_alt': ["https://porndune.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/en"))

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/en/videos/page/1?sort=date&time=anytime", order="date", page="0"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/en/videos/page/1?sort=popular&time=anytime", order="popular", page="0"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/en/videos/page/1?sort=rating&time=anytime", order="rating", page="0"))
    # itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "/most-commented/1/?sort_by=most_commented_month&from=01"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/models/?sort_by=avg_videos_popularity&from=01"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/sites/?sort_by=avg_videos_popularity&from=01"))

    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/en/categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%s/search/%s/" % (host,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []



# <div class="movie-panel mb-4">
# <div class="panel-img mb-1">
# <a href="https://porndune.com/en/category/amateur">
# <img src="/assets/images/no-image.png" alt="Amateur" class="img-fluid listImgs" style="display: inline;">
# </a>
# </div>
# <div class="movie-panel-title"><a href="https://porndune.com/en/category/amateur" class="text-secondary"><span class="float-right"><i class="fas fa-video"></i> 473</span> Amateur</a></div>
# </div>


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='movie-panel')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = ""
        cantidad = elem.find('span', class_='float-right')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
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
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


# <div class="col-lg-6 col-md-6 col-sm-6 col-xs-12 col-thumb panel-video-190774">
    # <div class="movie-panel mb-5" itemscope="" itemtype="http://schema.org/Movie">
    # <meta itemprop="name" content="Kill Bill: A XXX Parody">
    # <meta itemprop="image" content="https://www.adultdvd4sale.com/images/secure/zoom/787633029188f.jpg">
    # <meta itemprop="datePublished" content="2019-04-06">
    # <div class="panel-img mb-1">
        # <a href="https://porndune.com/en/watch/kill-bill-a-xxx-parody-porn-movie-free?v=lgPr4cETA0">
            # <img data-id="38cca372e54d296eb6da01dc5004d362" src="https://www.adultdvd4sale.com/images/secure/zoom/787633029188f.jpg" alt="Kill Bill: A XXX Parody" class="img-fluid listImgs" style="display: inline;">
                        # <video loop="true" muted="true" preload="none" class="preview_player" src="/files/teasers/preparing.mp4" data-active="0" onplaying="preview_onplay(this)" onerror="this.src='/files/teasers/preparing.mp4'" style="display: none;"></video>
            # <img src="/assets/themes/safari/images/preview-loader.gif" class="preview_loader" alt="loading..." style="display: none;">
                    # </a>
            # </div>
    # <div class="movie-panel-meta">
        # <div class="movie-panel-title mb-1" itemprop="potentialAction" itemscope="" itemtype="http://schema.org/WatchAction">
            # <a itemprop="target" href="https://porndune.com/en/watch?v=lgPr4cETA0" class="text-secondary">
                # Kill Bill: A XXX Parody            </a>
        # </div>

        
                # <div class="small text-secondary font-weight-light clearfix">
            # <div class="float-left mr-2">
                # <i class="fas fa-eye"></i> 40,299            </div>
            # <div class="float-left mr-2">
                # <i class="fa fa-heart text-danger"></i> 441            </div>
            # <div class="float-left mr-2">
                                # <a href="javascript:void(0);" data-id="190774" data-toggle="tooltip" data-placement="top" title="Add to playlist" id="watch-190774" class="auth-user save-watch-list">
                    # <span id="watch-span-190774"><i class="fas fa-plus-circle"></i></span> Playlist                </a>
                            # </div>

            # <div class="float-right movie-panel-watched rounded mr-2" id="watched-190774" data-toggle="tooltip" data-placement="top" title="Watched">
                # <i class="fas fa-video"></i>
            # </div>
        # </div>
                    # </div>
# </div>
    # </div>

# <li class="page-item text-center fixed-w-100"><a href="https://porndune.com/en/videos/page/2?sort=rating&amp;time=anytime" class="page-link" data-ci-pagination-page="2" rel="next">Next ›</a></li>




def lista(item):
    logger.info()
    itemlist = []
    sp = create_soup(item.url)
    posturl = "https://porndune.com/data/getVideos"
    post = "offset=%s&perpage=28&order=%s&sort=all&tag=0&keyword=" %(item.page, item.order)
    headers = {"Content-Length": "56", "x-requested-with": "XMLHttpRequest"}
    data = httptools.downloadpage(posturl, headers=headers,  post=post).json
    data = data['html']
    # logger.debug(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    matches = soup.find_all('div', class_='movie-panel')
    for elem in matches:
        # logger.debug(soup)
        url = elem.a['href']
        url = url.replace("watch/[A-z0-9-]+", "watch/")
        url = url.split('?')
        url = "%s/en/watch/?%s" %(host,url[-1])
        logger.debug(url)
        title = elem.img['alt']
        thumbnail = elem.img['data-src']
        # time = elem.find('span', class_='label time').text.strip()
        # quality = elem.find('span', class_='label hd')
        # if quality:
            # title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        # else:
            # title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = sp.find('a', rel='next')
    if next_page:
        next_page = next_page['href']
        page = int(item.page)
        item.page = (page+ 28)
        # next_page = re.sub(r"&offset=\d+", "&offset={0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist



# https://porndune.com/data/embed
# <iframe id="tubeplayer" class="resizeFrame" src="https://trafficdepot.xyz/v/y0z02fed4340mmn" width="100%" height="auto" frameborder="0" allowfullscreen></iframe>

# https://trafficdepot.xyz/v/y0z02fed4340mmn
# https://trafficdepot.xyz/api/source/y0z02fed4340mmn  #?r=&d=trafficdepot.xyz
# post = {'r':, 'd': 'trafficdepot.xyz'}


def play(item):
    logger.info()
    itemlist = []
    # soup = create_soup(item.url)
    # matches = soup.find('div', class_='tagged-videos')
    # offset = matches['data-offset']
    # perpage = matches['data-perpage']
    # tag= matches['data-tag']
    # vid = matches['data-vid']
    # css = matches['data-css']
    data = httptools.downloadpage(item.url).data
    vid = scrapertools.find_single_match(data, "var vid = (\d+);")
    hid = scrapertools.find_single_match(data, "var hid = (\d+);")    

    posturl = "https://porndune.com/data/embed"
    post= {"vid": vid, "hid": hid, "type": "video"}
    headers = {"X-Requested-With": "XMLHttpRequest", "Referer": item.url}
    data = httptools.downloadpage(posturl, headers = headers, post=post).data
    logger.debug(data)


    # data = httptools.downloadpage(posturl, headers=headers,  post=post).json
    # data = data['html']
    # soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    # logger.debug(soup)
    # url = soup.video['src']
    # logger.debug(url)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

