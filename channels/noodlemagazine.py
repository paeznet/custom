# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from core import jsontools
from bs4 import BeautifulSoup

forced_proxy_opt = ''
timeout = 45


# https://mat6tube.com/   https://noodlemagazine.com/  https://ukdevilz.com/

 ### thumbnail  CCurlFile::Stat - Failed: HTTP response code said error(22)
# <img src="https://img.pvvstream.pro/preview/BbDMDyFWwr10ofRck_xscQ/-227168778_456239029/i.mycdn.me/getVideoPreview?id=7228484618771&amp;idx=5&amp;type=39&amp;tkn=Qhaef9-RaSpD7Jye6ZYVkfJPE10&amp;fn=vid_l" data-src="https://img.pvvstream.pro/preview/BbDMDyFWwr10ofRck_xscQ/-227168778_456239029/i.mycdn.me/getVideoPreview?id=7228484618771&amp;idx=5&amp;type=39&amp;tkn=Qhaef9-RaSpD7Jye6ZYVkfJPE10&amp;fn=vid_l" class=" ls-is-cached lazyloaded" alt="[onlyfans] chloewildd hardcore anal and blowjob [pov, butt plug, big tits, anal, rough, facial, hardcore]">
# <img src="https://img.pvvstream.pro/preview/7vGaLMgpo-kZUfMK1gdrzA/-227259587_456239046/sun9-80.userapi.com/impg/wN7QPVcbAT99-EY0cOPuuc2LzOCH6p_xR3dYqw/bNkEgtVRYU0.jpg?size=320x240&amp;quality=95&amp;keep_aspect_ratio=1&amp;background=000000&amp;sign=5c2644ba33fa3a0043ec27d7af17e0df&amp;c_uniq_tag=ystg_EbYoe6Ln5msEr1m-7UIsWaBxq0rb0kdlma-U0w&amp;type=video_thumb" data-src="https://img.pvvstream.pro/preview/7vGaLMgpo-kZUfMK1gdrzA/-227259587_456239046/sun9-80.userapi.com/impg/wN7QPVcbAT99-EY0cOPuuc2LzOCH6p_xR3dYqw/bNkEgtVRYU0.jpg?size=320x240&amp;quality=95&amp;keep_aspect_ratio=1&amp;background=000000&amp;sign=5c2644ba33fa3a0043ec27d7af17e0df&amp;c_uniq_tag=ystg_EbYoe6Ln5msEr1m-7UIsWaBxq0rb0kdlma-U0w&amp;type=video_thumb" class=" ls-is-cached lazyloaded" alt="Diann ornelas onlyfans big tits большие сиськи big tits [трах, all sex, porn, big tits, milf, инцест, порно blowjob hot">

canonical = {
             'channel': 'noodlemagazine', 
             'host': config.get_setting("current_host", 'noodlemagazine', default=''), 
             'host_alt': ["https://noodlemagazine.com/"], 
             'host_black_list': [], 
             # 'set_tls': False, 'set_tls_min': False, 'retries_cloudflare': 6, 'cf_assistant': False, 
             # 'CF': False, 'CF_test': False, 'alfa_s': True
             'set_tls': None, 'set_tls_min': False, 'retries_cloudflare': 5, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'cf_assistant': False, 'CF_stat': True, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]




def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Buscar Nuevos" , action="search", ver=0))
    # itemlist.append(Item(channel=item.channel, title="Buscar Mas vistos" , action="search", ver=3))
    itemlist.append(Item(channel=item.channel, title="Buscar Mejor valorados" , action="search", ver=2))
    itemlist.append(Item(channel=item.channel, title="Buscar Mas largos" , action="search", ver=1))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%svideo/%s?sort=%s&p=0" % (host, texto, item.ver)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical, timeout=timeout).data
    else:
        data = httptools.downloadpage(url, canonical=canonical, timeout=timeout).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_="item")
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['data-src']  ### CCurlFile::Stat - Failed: HTTP response code said error(22)
        
        if 'getVideoPreview' in thumbnail:
            i1, i2 = thumbnail.split('/getVideoPreview')
            thumbnail = 'https://' + i1.split('/')[-1] + '/getVideoPreview' + i2
        thumbnail = thumbnail.replace('&amp;', '&')
        time = elem.find('div', class_='m_time').text.strip()
        quality = elem.find('i', class_='hd_mark')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                                   plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('div', class_='more')
    if next_page:
        current_page = scrapertools.find_single_match(item.url, ".*?=(\d+)")
        page = scrapertools.find_single_match(item.url, "(.*?)=\d+")
        current_page = int(current_page)
        current_page += 1
        next_page = "%s=%s" % (page, current_page)
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(item.url, canonical=canonical, timeout=timeout).data
    # url = scrapertools.find_single_match(data, '"embedUrl":\s*"([^"]+)"')
    # data = httptools.downloadpage(url, canonical=canonical, timeout=timeout).data
    patron = '\{"file":\s*"([^"]+)".*?'
    patron += '"label":\s*"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url,quality in matches:
        url += "|Referer=%s" %host
        itemlist.append(Item(channel=item.channel, action="play", title= "%s" %quality, contentTitle = item.title, url=url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

# "file":"https://cdn-pr.pvvstream.pro/videos/1080/-227355247_456242539.mp4?url=dmt2ZDQwOS5va2Nkbi5ydS8_c3JjSXA9NDUuODQuMzEuMTIxJnByPTQwJmV4cGlyZXM9MTc0NzEwOTE5ODc2MCZzcmNBZz1VTktOT1dOJmZyb21DYWNoZT0xJm1zPTQ1LjEzNi4yMC4xNjkmdHlwZT01JnNpZz1rUEYxbmo5SGU5ayZjdD0wJnVybHM9MTg1LjIyNi41My4yMDMmY2xpZW50VHlwZT0xNCZhcHBJZD01MTIwMDAzODQzOTcmaWQ9ODE1NzA5Nzk1Mzk3OA&secure=1746649998-qRIG6EwaZkKIGE5WnttNozK2rTZlKa8ClY5FmAomp1M%3D","label":"1080","type":"mp4"
def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical, timeout=timeout).data
    # url = scrapertools.find_single_match(data, '"embedUrl":\s*"([^"]+)"')
    # data = httptools.downloadpage(url, canonical=canonical, timeout=timeout).data
    patron = '\{"file":\s*"([^"]+)".*?'
    patron += '"label":\s*"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url,quality in matches:
        url += "|Referer=%s" %host
        itemlist.append(['%s' %quality, url])
    itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return itemlist
