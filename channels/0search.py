# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, jsontools, tmdb
from core import servertools, channeltools
from channelselector import get_thumb
from bs4 import BeautifulSoup

# https://api.themoviedb.org/3/movie/popular?api_key=a1ab8b8669da03637a4b98fa39c39228&language=es&page=1
canonical = {
             'channel': '0search', 
             'host': config.get_setting("current_host", '0search', default=''), 
             'host_alt': ["https://api.themoviedb.org/"], 
             'host_black_list': [], 
             # 'pattern': ['href="?([^"|\s*]+)["|\s*]\s*rel="?stylesheet"?'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

# __channel__='0search'

# parameters = channeltools.get_channel_parameters(__channel__)
# unif = parameters['force_unify']


def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, action='discover_list', title=config.get_localized_string(70307), search_type='list', list_type='movie/popular', mode='movie', thumbnail=get_thumb("popular.png")))
    itemlist.append(Item(channel=item.channel, action='discover_list', title=config.get_localized_string(70308), search_type='list', list_type='movie/top_rated', mode='movie', thumbnail=get_thumb("top_rated.png")))
    itemlist.append(Item(channel=item.channel, action='discover_list', title=config.get_localized_string(70309), search_type='list', list_type='movie/now_playing', mode='movie', thumbnail=get_thumb("now_playing.png")))
    
    itemlist.append(Item(channel=item.channel, action='discover_list', title=config.get_localized_string(70311), search_type='list', list_type='tv/popular', mode='tvshow', thumbnail=get_thumb("popular.png")))
    itemlist.append(Item(channel=item.channel, action='discover_list', title=config.get_localized_string(70313), search_type='list', list_type='tv/top_rated', mode='tvshow', thumbnail=get_thumb("top_rated.png")))
    itemlist.append(Item(channel=item.channel, action='discover_list', title=config.get_localized_string(70312), search_type='list', list_type='tv/on_the_air', mode='tvshow', thumbnail=get_thumb("on_the_air.png")))

    
    return itemlist

# def mainlist(item):
    # logger.info()

    # itemlist = [Item(channel=item.channel, title=config.get_localized_string(70741) % config.get_localized_string(30122), action='new_search', mode='movie', thumbnail=get_thumb("search.png")),

                # Item(channel=item.channel, title=config.get_localized_string(70741) % config.get_localized_string(30123), action='new_search', mode='tvshow', thumbnail=get_thumb("search_tvshow.png")),

                # Item(channel=item.channel, title=config.get_localized_string(70276), action='new_search', mode='all', thumbnail=get_thumb("search_generic.png")),

                # Item(channel=item.channel, title=config.get_localized_string(70741) % config.get_localized_string(70314), action='new_search', page=1, mode='person', thumbnail=get_thumb("search_star.png")),

                # Item(channel=item.channel, title=config.get_localized_string(59995), action='saved_search', thumbnail=get_thumb('folder.png')),

                # Item(channel=item.channel, title=config.get_localized_string(60420), action='sub_menu', thumbnail=get_thumb('search_more.png')),

                # Item(channel=item.channel, title=config.get_localized_string(59994), action='opciones', thumbnail=get_thumb('setting_0.png')),

                # Item(channel=item.channel, title=config.get_localized_string(30100), action='settings', thumbnail=get_thumb('setting_0.png'))]

    # itemlist = set_context(itemlist)


    # return itemlist


# def sub_menu(item):
    # logger.info()

    # itemlist = [Item(channel=item.channel, action='genres_menu', title=config.get_localized_string(70306), mode='movie', thumbnail=get_thumb("genres.png")),

                # Item(channel=item.channel, action='years_menu', title=config.get_localized_string(70742), mode='movie', thumbnail=get_thumb("years.png")),

                # Item(channel=item.channel, action='discover_list', title=config.get_localized_string(70307), search_type='list', list_type='movie/popular', mode='movie', thumbnail=get_thumb("popular.png")),

                # Item(channel=item.channel, action='discover_list', title=config.get_localized_string(70308), search_type='list', list_type='movie/top_rated', mode='movie', thumbnail=get_thumb("top_rated.png")),

                # Item(channel=item.channel, action='discover_list', title=config.get_localized_string(70309), search_type='list', list_type='movie/now_playing', mode='movie', thumbnail=get_thumb("now_playing.png")),

                # Item(channel=item.channel, action='genres_menu', title=config.get_localized_string(70310), mode='tvshow', thumbnail=get_thumb("genres.png")),

                # Item(channel=item.channel, action='years_menu', title=config.get_localized_string(70743), mode='tvshow', thumbnail=get_thumb("years.png")),

                # Item(channel=item.channel, action='discover_list', title=config.get_localized_string(70311), search_type='list', list_type='tv/popular', mode='tvshow', thumbnail=get_thumb("popular.png")),

                # Item(channel=item.channel, action='discover_list', title=config.get_localized_string(70312), search_type='list', list_type='tv/on_the_air', mode='tvshow', thumbnail=get_thumb("on_the_air.png")),

                # Item(channel=item.channel, action='discover_list', title=config.get_localized_string(70313), search_type='list', list_type='tv/top_rated', mode='tvshow', thumbnail=get_thumb("top_rated.png")),

                # Item(channel="tvmoviedb", action="mainlist", title=config.get_localized_string(70274), thumbnail=get_thumb("search_more.png"))]

    # itemlist = set_context(itemlist)

    # return itemlist




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


def discover_list(item):
    import datetime
    from platformcode import unify
    
    itemlist = []
    
    year = 0
    if item.discovery and not item.discovery.get("language", ""):
        item.discovery["language"] = def_lang
    tmdb_inf = tmdb.discovery(item, dict_=item.discovery, cast=item.cast_)
    result = tmdb_inf.results
    tvshow = False
    
    for elem in result:
        elem = tmdb_inf.get_infoLabels(elem, origen=elem)
        if 'title' in elem:
            title = unify.normalize(elem['title']).capitalize()
        else:
            title = unify.normalize(elem['name']).capitalize()
            tvshow = True
        elem['tmdb_id'] = elem['id']
        
        mode = item.mode or elem['media_type']
        thumbnail = elem.get('thumbnail', '')
        fanart = elem.get('fanart', '')
        
        if item.cast_:
            release = elem.get('release_date', '0000') or elem.get('first_air_date', '0000')
            year = scrapertools.find_single_match(release, r'(\d{4})')
            
        if not item.cast_ or (item.cast_ and (int(year) <= int(datetime.datetime.today().year))):
            # new_item = Item(channel='search', title=title, infoLabels=elem,
            new_item = Item(channel='item.channel', title=title, infoLabels=elem,
                            action='channel_search', text=title,
                            thumbnail=thumbnail, fanart=fanart,
                            context='', mode=mode,
                            release_date=year)
            
            if tvshow:
                new_item.contentSerieName = title
            else:
                new_item.contentTitle = title

            itemlist.append(new_item)

    itemlist = set_context(itemlist)

    if item.cast_:
        itemlist.sort(key=lambda it: int(it.release_date), reverse=True)
        return itemlist

    elif len(result) > 19 and item.discovery:
        item.discovery['page'] = str(int(item.discovery['page']) + 1)
        itemlist.append(Item(channel=item.channel, action='discover_list', title=config.get_localized_string(70065),
                             list_type=item.list_type, discovery=item.discovery, mode=item.mode, text_color='gold'))
    elif len(result) > 19:
        next_page = str(int(item.page) + 1)

        itemlist.append(Item(channel=item.channel, action='discover_list', title=config.get_localized_string(70065),
                             list_type=item.list_type, search_type=item.search_type, mode=item.mode, page=next_page,
                             text_color='gold'))

    return itemlist


def set_context(itemlist):
    logger.info()

    for elem in itemlist:
        elem.context = [{"title": config.get_localized_string(60412),
                         "action": "setting_channel_new",
                         # "channel": "search"},
                         "channel": "item.channel"},
                        {"title": config.get_localized_string(60415),
                         "action": "settings",
                         # "channel": "search"},
                         "channel": "item.channel"},
                        {"title": config.get_localized_string(60416),
                         "action": "clear_saved_searches",
                         # "channel": "search"}
                         "channel": "item.channel"}]

    return itemlist



def channel_search(item):
    logger.info(item)
    from concurrent import futures

    start = time.time()
    preliminary_results = dict()
    results = list()
    valid = list()
    mode = item.mode
    max_results = 10
    item.text = item.contentSerieName or item.contentTitle or item.text

    searched_id = item.infoLabels['tmdb_id']

    channel_ids, channel_names = get_channels(item)

    searched_channels = dict(zip(channel_ids, channel_names))
    completed_cnt = 0
    total_channels = len(channel_ids)
    # tm = 20 + len(channel_names)

    message = config.get_localized_string(70744) % str(total_channels)
    message = '%s\n(%s)' % (message, ", ".join(searched_channels.values()))
    progress = dialog_progress(config.get_localized_string(30993) % '"{}"'.format(item.title), message)
    config.set_setting('tmdb_active', False)

    with futures.ThreadPoolExecutor(max_workers=set_workers()) as executor:
        tasks = [executor.submit(get_channel_results, ch, item) for ch in channel_ids]

        try:
            while completed_cnt < total_channels and not progress.iscanceled():
                completed_id = ""
                for task in tasks:
                    if task.done():
                        result = task.result()
                        completed_id = result[0]
                        if searched_channels.get(completed_id):
                            searched_channels.pop(completed_id)
                            if isinstance(result[1], list):
                                preliminary_results[completed_id] = result[1]
                            else:
                                preliminary_results[completed_id] = []
                            completed_cnt += 1

                percent = (completed_cnt * 100) // total_channels
                text1 = config.get_localized_string(70744) % str(total_channels - completed_cnt)
                text2 = "({0})".format(", ".join(searched_channels.values()))
                
                if PY3:
                    progress.update(percent, "{0}\n{1}".format(text1, text2))
                else:
                    progress.update(percent, text1, text2, ' ')

                if progress.iscanceled():
                    if sys.version_info >= (3, 8):
                        executor.shutdown(wait=False, cancel_futures=True)
                    else:
                        executor.shutdown(wait=False)
                        for f in tasks:
                            f.cancel()
                    raise Exception('## Búsqueda global cancelada por el usuario')
                
                time.sleep(0.2)

        except Exception as err_msg:
            logger.error('Error "%s"' % (err_msg))
            executor.shutdown(wait=False)
            config.GLOBAL_SEARCH_CANCELLED = True
            for key, cha in list(channel_parameters_list.items()):
                if cha.get('module'):
                    try:
                        cha['module'].canonical['global_search_cancelled'] = True
                    except:
                        pass

    progress.close()

    completed_cnt = 0
    progress = dialog_progress(config.get_localized_string(30993) % item.title, config.get_localized_string(60295),
                               config.get_localized_string(60293))

    if not config.get_setting('tmdb_active'): config.set_setting('tmdb_active', True)
    res_count = 0
    for key, value in list(preliminary_results.items()):
        ch_name = channel_names[channel_ids.index(key)]
        grouped = list()
        completed_cnt += 1
        progress.update(old_div((completed_cnt * 100), len(preliminary_results)), config.get_localized_string(60295) \
                        + '\n' + config.get_localized_string(60293))
        if len(value) <= max_results and item.mode != 'all':
            if len(value) == 1:
                if not value[0].action or config.get_localized_string(70006).lower() in value[0].title.lower():
                    continue
            tmdb.set_infoLabels_itemlist(value, True, forced=True)
            for elem in value:
                if "-Próximamente-" in elem.title:
                    continue

                if not elem.infoLabels.get('year', "") and not elem.infoLabels.get('filtro', ""):
                    elem.infoLabels['year'] = '-'
                    tmdb.set_infoLabels_item(elem, True)

                if elem.infoLabels['tmdb_id'] == searched_id:
                    elem.from_channel = key
                    
                    if not config.get_setting('unify'):
                        elem.title = '[%s] %s' % (key.capitalize(), elem.title)
                    valid.append(elem)

        for it in value:
            if it.channel == item.channel:
                it.channel = key
            if it in valid or "-Próximamente-" in it.title:
                continue
            if mode == 'all' or (it.contentType and mode == it.contentType):
                if not it.infoLabels or not item.text.lower() in it.title.lower():
                    continue
                if config.get_setting('search_result_mode') != 0:
                    if config.get_localized_string(30992) not in it.title:
                        it.title += " " + ch_name
                        results.append(it)
                else:
                    grouped.append(it)
            elif (mode == 'movie' and it.contentTitle) or (mode == 'tvshow' and (it.contentSerieName or it.show)):
                grouped.append(it)
            else:
                continue

        if not grouped:
            continue
        # to_temp[key] = grouped
        if config.get_setting('search_result_mode') == 0:
            if not config.get_setting('unify'):
                title = ch_name + ' [COLOR yellow](' + str(len(grouped)) + ')[/COLOR]'
            else:
                title = '[COLOR yellow](%s)[/COLOR]' % (len(grouped))
            res_count += len(grouped)
            plot=''

            for it in grouped:
                plot += it.title +'\n'
            ch_thumb = channeltools.get_channel_parameters(key)['thumbnail']
            results.append(Item(channel='search', title=title,
                                action='get_from_temp', thumbnail=ch_thumb, itemlist=[ris.tourl() for ris in grouped], 
                                plot=plot, page=1, from_channel=key))

    # send_to_temp(to_temp)
    if not config.get_setting('tmdb_active'): config.set_setting('tmdb_active', True)
    if item.mode == 'all':
        if config.get_setting('search_result_mode') != 0:
            res_count = len(results)
        results = sorted(results, key=lambda it: it.title)
        results_statistic = config.get_localized_string(59972) % (item.title, res_count, time.time() - start)
        results.insert(0, Item(title = results_statistic))
    # logger.debug(results_statistic)
    
    return valid + results


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
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist



def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    pornstars = soup.find_all('a', href=re.compile("/models/[A-z0-9-]+/"))
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    lista = item.contentTitle.split()
    if "HD" in item.title:
        lista.insert (4, pornstar)
    else:
        lista.insert (2, pornstar)
    item.contentTitle = ' '.join(lista)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
