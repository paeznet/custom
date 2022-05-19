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
from core import jsontools
from bs4 import BeautifulSoup

canonical = {
             'channel': 'tube8', 
             'host': config.get_setting("current_host", 'tube8', default=''), 
             'host_alt': ["https://www.tube8.com"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s*rel="?stylesheet"?'], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/newest.html"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/mostviewed.html"))
    itemlist.append(Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "/most-popular/?sort_by=video_viewed_week"))
    # itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "/videos?type=public&o=md"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/top-rated/?sort_by=rating_week"))
    # itemlist.append(Item(channel=item.channel, title="Mas metraje" , action="lista", url=host + "/videos/straight/all-length.html"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="catalogo", url=host + "/pornstars/?sort=rl"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/channels/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories.html"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search/video/%s" % (host,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []



        # <div class="popular_pornstars_wrapper" data-esp-node="popular_pornstars">
            # <div class="gridList" id="popular_pornstars_wrapper" data-cols="10">
                # <div class="pornstar-box content-wrapper" data-esp-node="pornstar_box">
    # <div class="pornstar-box-inner">
        # <div class="rank-box">
            # <span>Rank</span>
            # <span class="rank-number">2339</span>
        # </div>
        # <div class="pornstar">
            # <a href="https://www.tube8.com/pornstar/jacky-lawless/89538931/">
                # <img class="js_lazy"
                     # src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="
                     # data-thumb="https://ei.phncdn.com/pics/pornstars/000/296/951/(m=lciKgBcOb_c)(mh=DiTFr_vOqfcKwPhj)thumb_1292541.jpg"
                     # alt="Jacky Lawless">
                # <ul class="pornstar-infos">
                    # <li class="pornstar-name">Jacky Lawless</li>
                    # <li class="pornstar-videos"><span>1</span> Videos</li>
                # </ul>
            # </a>
        # </div>
    # </div>
# </div>


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_='popular_pornstars_wrapper').find_all('div', class_='pornstar')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['data-thumb']
        cantidad = elem.find('li', class_='pornstar-videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', id='pagination_next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist



# <li>
						# <a href="https://www.tube8.com/cat/hd/22/" data-esp-node="category_box">
							# <div class="flexRatio" data-size="330x250">
                                # <img class="js_lazy loaded" src="https://es.t8cdn.com/images/categories/general/0/22_hq.jpg?cache=a745aa6271e18965b24a299c38612f36930da4b2" alt="hd" data-ll-status="loaded">
							# </div>
							# <h5>HD <span>(150424)</span></h5>
						# </a>
                    # </li>


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('ul', id='porn-categories-box')
    matches = soup.find_all('li')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('h5').text
        thumbnail = elem.img['src']
        # if not thumbnail:
            # thumbnail = elem.a['src']

        cantidad = elem.find('div', class_='videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        # if "popular" in url:
            # url = url.replace("popular", "recent")
        # if "profile" in url:
            # url += "/videos/"
        # url = urlparse.urljoin(item.url,url)
        # url += "?type=public&o=mr"
        # thumbnail = urlparse.urljoin(item.url,thumbnail)
        # thumbnail = ""
        # plot = ""
        # if not "/galleries/" in url:
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, fanart=thumbnail, thumbnail=thumbnail) )
    next_page = soup.find('li', class_='next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url).data
        data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup



# <figure class="video_box " data-esp-node="video_box" data-video_url="https://www.tube8.com/public/horny-chav-teen-sucks-cock-and-takes-huge-facial-in-public-underpass-she-cant-help-being-a-whore/81230461/" data-videoid="i81230461" id="boxVideo_i81230461">       
 # <div class="thumb_box" id="video_i81230461">              
 # <a class="js-pop video-thumb-link" href="https://www.tube8.com/public/horny-chav-teen-sucks-cock-and-takes-huge-facial-in-public-underpass-she-cant-help-being-a-whore/81230461/">                            
 # <div class="videoThumbsWrapper" data-size="400x225">                                            
 # <img alt="Horny chav teen sucks cock and takes HUGE facial in public underpass - She cant help being a whore!" class="js_lazy lazyMenu videoThumbs js-flipBook " data-mediabook="" data-thumb="https://ei3.t8cdn.com/videos/202008/12/341753761/original/14(m=eqw4mgaaaa)(mh=6T3N1jKKrp_0L1rH).jpg" id="i81230461" src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=" title="Horny chav teen sucks cock and takes HUGE facial in public underpass - She cant help being a whore!"/>                            </div>                            </a>        <span class="video-attributes-features">                <span class="hdIcon">HD</span>            <span class="esp_video_quality">720p</span>                    <span class="verified-amateur"><span class="icon-check-alt"></span></span>        </span><span class="video-attribute-duration">    <span class="video-duration">07:16</span></span>    </div>    <figcaption>            <p class="video-title">        <a class="js-pop video-title-link" data-esp-node="video_title" href="https://www.tube8.com/public/horny-chav-teen-sucks-cock-and-takes-huge-facial-in-public-underpass-she-cant-help-being-a-whore/81230461/" title="Horny chav teen sucks cock and takes HUGE facial in public underpass - She cant help being a whore!">            Horny chav teen sucks cock and takes HUGE facial in public underpass - She cant help being a whore!        </a>    </p>    <p class="video-attributes">        <span class="video-views">            <span class="icon-video-views"></span>            4k        </span>                                                                        <span class="content-partner">                    <a class="js-pop" data-esp-node="content_partner_video" href="https://www.tube8.com/user-videos/82789261/Angel_Savage/" target="_blank" title="Angel_Savage">                        Angel_Savage                    </a>                </span>                        </p>    </figcaption></figure>

# <figure class="video_box " data-esp-node="video_box" data-video_url="https://www.tube8.com/hardcore/homemade-gf-multiple-orgasmns/81230721/" data-videoid="i81230721" id="boxVideo_i81230721">        
    # <div class="thumb_box" id="video_i81230721">                
    # <a class="js-pop video-thumb-link" href="https://www.tube8.com/hardcore/homemade-gf-multiple-orgasmns/81230721/">                            
    # <div class="videoThumbsWrapper" data-size="400x225">                                            
    # <img alt="HOMEMADE GF MULTIPLE ORGASMNS" class="js_lazy lazyMenu videoThumbs js-flipBook " data-mediabook="" data-thumb="https://ei3.t8cdn.com/videos/201904/15/218488021/original/9(m=eqw4mgaaaa)(mh=utHCVgpqiNd8AItH).jpg" id="i81230721" src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=" title="HOMEMADE GF MULTIPLE ORGASMNS"/>                            </div>                            </a>       
    # <span class="video-attributes-features">                <span class="hdIcon">HD</span>           
    # <span class="esp_video_quality">720p</span>                    <span class="verified-amateur"><span class="icon-check-alt"></span></span>        </span><span class="video-attribute-duration"> 
    # <span class="video-duration">26:58</span></span>    </div>    <figcaption>            <p class="video-title">        <a class="js-pop video-title-link" data-esp-node="video_title" href="https://www.tube8.com/hardcore/homemade-gf-multiple-orgasmns/81230721/" title="HOMEMADE GF MULTIPLE ORGASMNS">            HOMEMADE GF MULTIPLE ORGASMNS        </a>    </p>    <p class="video-attributes">        <span class="video-views">            <span class="icon-video-views"></span>            0        </span>                                                                        <span class="content-partner">                    <a class="js-pop" data-esp-node="content_partner_video" href="https://www.tube8.com/user-videos/83061761/JAfuntime/" target="_blank" title="JAfuntime">                        JAfuntime                    </a>                </span>                        </p>    </figcaption></figure>



# <li><strong><a href="https://www.tube8.com/newest/page/2/" id="pagination_next"><i class="icon-chevron-right"></i></a></strong></li>


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('figure', id=re.compile(r"^boxVideo_i\d+"))
    logger.debug(soup)

    for elem in matches:
        # logger.debug(elem)
        url = elem.a['href']
        title = elem.img['alt'] #elem.find('p', class_='video-title').text.strip() #.a['title']
        thumbnail = elem.img['data-thumb']
        # thumbnail = scrapertools.find_single_match(thumbnail, 'url\(([^\)]+)')
        # logger.debug(thumbnail)

        quality = elem.find('span', class_='esp_video_quality')
        time = elem.find('span', class_='video-duration').text.strip()
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (time, quality.text.strip(), title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        # referer = urlparse.urljoin(item.url,referer)
        # if not thumbnail.startswith("https"):
            # thumbnail = "https:%s" % thumbnail
        # url = "https://www.amateur.tv/ajax/freecamView/camId/%s/mode/public" % id
        url += "|Referer=%s" % url
        # thumbnail= ""
        # plot = ""
        itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, contentTitle=title,
                                   fanart=thumbnail, thumbnail=thumbnail ))

    next_page = soup.find('a', id='pagination_next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title=next_page, url=next_page) ) #"[COLOR blue]Página Siguiente >>[/COLOR]"
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('source')['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


# "videoServers":{"flash":["rtmp:\/\/51.178.89.193:1935\/obs_rep_31.170.103.163?t=201221151311692156-TV_2752425-1608564383423-y2rUC2gSdFw5iYpRDOviT0onKSnJbr1JNlYCe4QBC2g%3D",
                         # "rtmp:\/\/51.178.89.192:1935\/obs_rep_31.170.103.163?t=201221151311692156-TV_2752425-1608564383424-UNpu9OvAc03ywwZZX4MMvnEQG20z5tVDW5qyrleBrE8%3D"],
                # "html5":["\/\/fr-edge12.vtsmedia.com\/obs_rep_31.170.103.163\/TV_2752425_hls\/playlist.m3u8?t=201221151311692156-TV_2752425-1608564383423-y2rUC2gSdFw5iYpRDOviT0onKSnJbr1JNlYCe4QBC2g%3D",
                         # "\/\/fr-edge11.vtsmedia.com\/obs_rep_31.170.103.163\/TV_2752425_hls\/playlist.m3u8?t=201221151311692156-TV_2752425-1608564383424-UNpu9OvAc03ywwZZX4MMvnEQG20z5tVDW5qyrleBrE8%3D"],
                   # "ws":["wss:\/\/ws.vtsmedia.com\/ws\/?t=Fku1e9-bRgrNGAzZA0EJSw2Y29eK3ZrLnpAN3Q3M20dLzdhMGIRAiQ7NmBuRjBzcyxzRyxyMzNsASo0Zyxh",
                         # "wss:\/\/ws.vtsmedia.com\/ws\/?t=P7CTEi-PQ53AgUTNBsSeRpTQz9Id0AODipWa0JSEz0LcwEEEDIHFHgNU0A-UGxFFgwjUXBEVhM8F3YCBQwx"],
              # "capohls":["\/\/hls.vtsmedia.com\/stream\/TV_2752425\/playlist.m3u8?t=eyJkIjp7InUiOiIyMDEyMjExNTEzMTE2OTIxNTYiLCJzIjoiXlRWXzI3NTI0MjUoPzpfaGlnaCk\/KD86X21lZCk\/JCIsImMiOjE2MDg1NjQ0MTMsImciOnRydWUsImEiOmZhbHNlfSwicyI6IjA2OThmODg4NTZhZDhhZjdhZWQwZTBhYmQ2MDJhYjZmM2NkZTA4Y2Q2YzE1YWE0YmJiYTZkMGQ5ZmM4Yzg4NzAifQ==",
                         # "\/\/hls.vtsmedia.com\/stream\/TV_2752425\/playlist.m3u8?t=eyJkIjp7InUiOiIyMDEyMjExNTEzMTE2OTIxNTYiLCJzIjoiXlRWXzI3NTI0MjUoPzpfaGlnaCk\/KD86X21lZCk\/JCIsImMiOjE2MDg1NjQ0MTMsImciOnRydWUsImEiOmZhbHNlfSwicyI6IjA2OThmODg4NTZhZDhhZjdhZWQwZTBhYmQ2MDJhYjZmM2NkZTA4Y2Q2YzE1YWE0YmJiYTZkMGQ5ZmM4Yzg4NzAifQ=="],
                # "hlsV2":["https:\/\/hls.vtsmedia.com\/stream\/TV_2752425\/playlist.m3u8?t=eyJkIjp7InUiOiIyMDEyMjExNTEzMTE2OTIxNTYiLCJzIjoiXlRWXzI3NTI0MjUoPzpfaGlnaCk\/KD86X21lZCk\/JCIsImMiOjE2MDg1NjQ0MTMsImciOnRydWUsImEiOmZhbHNlfSwicyI6IjA2OThmODg4NTZhZDhhZjdhZWQwZTBhYmQ2MDJhYjZmM2NkZTA4Y2Q2YzE1YWE0YmJiYTZkMGQ5ZmM4Yzg4NzAifQ==",
                         # "https:\/\/hls.vtsmedia.com\/stream\/TV_2752425\/playlist.m3u8?t=eyJkIjp7InUiOiIyMDEyMjExNTEzMTE2OTIxNTYiLCJzIjoiXlRWXzI3NTI0MjUoPzpfaGlnaCk\/KD86X21lZCk\/JCIsImMiOjE2MDg1NjQ0MTMsImciOnRydWUsImEiOmZhbHNlfSwicyI6IjA2OThmODg4NTZhZDhhZjdhZWQwZTBhYmQ2MDJhYjZmM2NkZTA4Y2Q2YzE1YWE0YmJiYTZkMGQ5ZmM4Yzg4NzAifQ=="]}




def play(item):
    logger.info()
    itemlist = []
    # soup = create_soup(item.url)
    # url = soup.find('source')['src']
    # data = httptools.downloadpage(item.url).data
    # url = scrapertools.find_single_match(data, '"hlsV2":\["([^"]+)"')
    # url = url.replace("\/", "/")
    # logger.debug(url)
            # itemlist.append(['.mp4 %s' %quality, url])
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
