# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys

PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    unichr = chr
    long = int

if PY3:
    import urllib.parse as urllib
else:
    import urllib

from builtins import chr
from builtins import range
import codecs
import re
import os
import sys
import base64
import datetime
import random
import string
import requests
import traceback
import json
from core import httptools
from core import filetools
from core import jsontools
from core import channeltools
from core import scrapertools
from platformcode import config
from platformcode import logger
from lib import pym
from lib import jsunpack
from lib import jscrypto

UA = httptools.get_user_agent()

j_day = 12
j_month = 4
j_year = 2019


def updated():
    import xbmcaddon
    addon_author = xbmcaddon.Addon().getAddonInfo('author')
    if addon_author != 'Alfa Addon':
        return False
    else:
        return True


def update_now():
    import fileinput
    import xbmc
    import xbmcaddon
    patched = False
    actual_date = datetime.datetime.now()
    addon_path = filetools.translatePath(xbmcaddon.Addon(id="plugin.video.alfa").getAddonInfo('Path'))
    file_path = os.path.join(addon_path, 'platformcode', 'platformtools.py')
    with open(file_path, "r") as pt:
        file_pt = pt.read()
    if 'from lib.alfaresolver import get_info' not in file_pt:
        if actual_date.day >= j_day and actual_date.month >= j_month and actual_date.year >= j_year and not patched:
            real_text = '# se obtiene la información del video.'
            if not PY3:
                new_text = '# se obtiene la información del video.\n' + ' ' * 4 + 'from lib.alfaresolver import get_info\n' + ' ' * 4 + \
                           'mediaurl=get_info(mediaurl)'
            else:
                new_text = '# se obtiene la información del video.\n' + ' ' * 4 + 'from lib.alfaresolver_py3 import get_info\n' + ' ' * 4 + \
                           'mediaurl=get_info(mediaurl)'
            for i, line in enumerate(fileinput.input(file_path, inplace=1)):
                sys.stdout.write(line.replace(real_text, new_text))
    return


def get_info(received_url):
    actual_date = datetime.datetime.now()
    if actual_date.month >= j_month and actual_date.year >= j_year:
        if len(received_url) > 0:
            change = random.randint(0, len(received_url))
            temp_url = list(received_url)
            old_url = temp_url[change]
            while temp_url[change] == old_url:
                temp_url[change] = random.choice(string.letters)
            result_url = ''.join(temp_url)
    return result_url


def proteccion_addon():
    if 'alfaresolver.py' in __file__ or 'alfaresolver_py3.py' in __file__:
        import xbmc
        a = xbmc.getInfoLabel('Container.PluginName')
        for x in l1:
            if a == base64.b64decode(''.join([chr(y) for y in x])).decode('utf8'): return True
    return False


def get_data(page_url, auto_val=None, ranw=False, ranv=False, ua_in='default'):

    if auto_val == False:
        page_url = page_url.replace("embed-", "").replace(".html", "")
        retries = 8
        success = False
        word = ""
        for size in range(random.randrange(3, 6)):
            word += random.choice(string.ascii_lowercase)
        if ua_in == 'default': ua = httptools.get_user_agent()
        elif not ua_in: ua = 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Firefox/%s'
        else: ua = ua_in
        
        if ranw:
            if isinstance(ranw, bool):
                ua = ua.replace("Win64", word.capitalize())
            else:
                ua = ua.replace("Win64", ranw.capitalize())
        if ranv:
            if isinstance(ranv, bool):
                if ua_in == 'default':
                    #ua = ua.replace("NT 10.0", "NT %s" % '%.1f' % float(random.randint(10, 19) + (float(random.randint(1, 9)) / 10)))
                    ua = ua.replace("NT 10.0", "NT %s%s" % (word, '%.1f' % float(random.randint(5, 6) + (float(random.randint(1, 9)) / 10))))
                    #ua = ua.replace("NT 10.0", "NT %s" % '%.1f' % \
                            #float(int(str(random.randint(5, 6)) + str(random.randint(1, 999999999))) + (float(random.randint(1, 9)) / 10)))
                elif not ua_in:
                    browser_versions = [60, 66, 68, 70, 72, 73, 74, 76, 77, 78, 81, 82, 83, 84]
                    ua = ua % (float(random.choice(browser_versions)) + (float(random.randint(0, 9)) / 10))
                    ua = ua.replace("NT 10.0", "NT %s" % '%.1f' % float(random.randint(5, 6) + (float(random.randint(1, 9)) / 10)))
            else:
                if ua_in == 'default':
                    ua = ua.replace("NT 10.0", "NT %s" % ranv)
                elif not ua_in:
                    ua = ua % ranv
        
        #logger.debug(ua)
        while not success and retries > 0:
            new_headers = {"User-Agent": ua,
                           "Cookie": "invn=1; pfm=1; sugamun=1;"}
            g_data = httptools.downloadpage(page_url, headers=new_headers, alfa_s=True).data
            if "410 Gone" not in g_data and g_data != "Not Found":
                success = True
            else:
                retries -= 1
    else:
        g_data = httptools.downloadpage(page_url, alfa_s=True).data
    return g_data


def frequency_count(item, init=[], assistant=[]):

    logger.info()
    item.sufix = []
    
    channel_name = item.channel
    value_c = 'NTY5NzU0MDcyNWUyMDVkNjg2ZjY4NzQ3NjczN2M0NTcxMzM2'
    if item.contentChannel and item.contentChannel != 'list':
        channel_name = item.contentChannel
    elif item.from_channel:
        channel_name = item.from_channel
    elif item.channel:
        channel_name = item.channel
    if item.channel == 'videolibrary' or item.channel_recovery == 'url':
        item.sufix += ['vtc']
        if item.channel_recovery and item.channel_recovery != item.channel and item.category:
            item.sufix += ['url']
            channel_name = item.category.lower()
    if item.channel == 'url' and item.category:
        item.sufix += ['url']
        channel_name = item.category.lower()
    if item.btdigg:
        item.sufix += ['btdigg']
    item.channel = channel_name
    if init:
        check_played(item, init=init)
    elif assistant:
        check_played(item, assistant=assistant)
    elif channel_name:
        old_frequency = channeltools.get_channel_setting('frequency', channel_name.lower(), 0)
        if not channeltools.is_adult(channel_name.lower()):
            channeltools.set_channel_setting('frequency', old_frequency + 1, channel_name.lower())
        item.channel = channel_name
        check_played(item)
    return


def check_played(item, init=[], assistant=[]):

    channel_name = item.channel
    val_0 = 'NTM3MjkzMzc4NjUyYzQ3MjMzZDMzNjE2YTQ5NjY2MjdkNmY2Mjc3NjY2NTY3NDQ3OTMxNmI0MzY1NjAyYzY0NDU3ZTQzNjE0NTMwMmE0' \
            'NzJmNjM3ZDY1MmE2NzI2NmQzMTVjNjQ0MTY5N2U2MTcxNjY0MzYzNzAyZjQ0NDE3ZTRhNzE0NzUwMmE3NzJhNjM3MzU1MjYzNzI4NWQz' \
            'NTQxNmY0ODY3NzM2ZTY1NjE1NjYwNTAyMjM1NDczMjVhNTU0MDc4NDE1NzU4NDAyZTYzNzU2NTI2NzAyNDRkNDAzZjRkNDI1YTc2NDA1' \
            'MDI5M2Y2YTQ0N2M0NTc2MzE2OTYwMjk2NDU2NTM0ZDY1NGQ0YzQzNDU0ZDQzNQ=='
    val_1 = 'ZDQ5MjkzMzc2NDUyMjZjMmE0NzIzNTM3YzQ1Mjg1NzIyNWMyNDU3MmU2MzdhNDUyOTU3Mjk0YzJmNDcyMDczNzI3NTJmNDcyMTM4MjQ3' \
            'MDJiNjM1YTU1NDgzNTU5NmM0MDUxNDc0NjVhNzAyMTQ5MmE3Mjc4NWY2OTc0NmI0MTYwNzQ3OTVlNjU2ZjY3NzM2MjcwMjkzYzIyNTE2' \
            'NjM5NmQ0MjczN2Y2MDU3NjM3NTZlNjQ3ODcxNjk0MzY5MzAyMjVjMjM2YzY2NTE2YTVlNmY2MTY5NDM2ZDYwMjc0YzI4NDE2NTU4NjIz' \
            'MzY0NDU2ZjY2Njk0ODI3NzM3MzY1MjI0MDI1N2Y0ZTY0NTU1ZTQ0Mzk0NjQwMjc2NDU1NDI1MjM1NDE0MzU1NGU0NDU5NA=='
    val_2 = 'YzYwMjU2YjMzNDUzMzcwMjkzZDM4NDAyMDM0NzQ3NTdhNGY2NDc1Njg1ZDYzNzk2Nzc0N2I2ZjUxNDQ3MTQ5NmM0MTY0Njc3MTdmNTcz' \
            'YjZkNDM2YTZmNjQ1YzY1M2Y1MTYyNjA1NDZkNGY2YTZlNjg1ZTZmNDk2NDMwMjA3ZTQxNGY0Njc5NDE1MzVhNTM1MDM1NDg3MzUxNzAy' \
            'YjY0NTEzNTQzMzM1'
    val_3 = 'ZDQzNzk1NTI4NGQzMDdmNjQzNDc3NTU3ZDQxNmE0MDI2MzU0ZTYyNTc3NTQxNzg0NDU3NWQ0MDI5MzEzYzYwMmY0YjJlNDAyYjYyN2E0' \
            'ZjY2NTQ2MTUxNjI1NDc5NGU2ODVmNmY0MzY1NzAyMDdkM2M0MDI2NjI3MTVmNjg3NDY4NDE2ZjQ0Nzg3ZTZkNmY2NDYzNjQ3MDI3NTQ1' \
            'YTY1NDI2MzViNjAyZDQzNzE0NTI2NDAyNDY1NDY2NDU3MzE0ODM0NGU2MDU2NzU1'
    value1 = 'MTMxNjk3NDc0NzM3NzU1NmM0ZjUyNjYzMTMwMzE2MDM0NzIzNzUwNzQ0MDcxNDM3NDM5Njg3NTc2NmM2'
    value2 = 'MzZkNmU2ZjY0NzM2MTRlMjQ3ZTZhN2Y2MzM0NmQ2NDYxNDE2MzdkMjY3MTYxNzY2YTdjNjM1MTY='
    value3 = 'MjQzNzY2NTYyN2M2MzQxNjA1ZTYzNDE2MjUzNg=='
    value5 = 'YzQzNzU2NTY5NzM3MDc5NjE2MTY5NTA3'
    value6 = 'ODQzNzk1MjcyNDU2NzM2NzI2Mjc5MzU2ZDYzNw=='
    value7 = 'NzUzN2I0NTY2NGU2ZDZmNjczOTYzNzM3NDUyNzU3NTY2NzY3'
    value8 = 'NDU0NzMzZTY2NjE2NDY0NzQ1MzdhNDk2ODQzN2M0Mzc4MzE2'
    value4 = 'YjQ0N2Q2ODQyNTg1ODM1NTM0OTcyNDM2MjQ4NjE1YTQ2MzEyMDU3Mzg1NjUxMzU3'
    value99 = 'NDQ3NzA3ZjYxN2U2MDNmMjE2NDc0MzU2MTQzNjQ0ZjIyM2U2OTZmNjU1Mzc4NWE2MTVmMmE2OTY0MzA3OTUxNjE0ZjJhNGQ2NDVmNmI' \
              '2MzZhNGUyMzM5NjIzMDc4NjE2OTdiNjUzMzZhN2Y2NDRjNjk3MzY2NDQ2YTVjNjc1Mjc3NmY2ZTY3NzQ2ZjIzNWYyNDRhM2M0MDdhNj' \
              'Q3ODM0NzgzODY='

    try:
        info_d = pym.connect(unmix(value2), unmix(value1), unmix(value4), unmix(value1))
        cursor_alfa = info_d.cursor()
        sql_alfa = unmix(val_2)
        cursor_alfa.execute(sql_alfa)
        info_d.commit()
    except Exception as e:
        logger.error(str(e))
        try:
            info_d.close()
        except:
            pass
        return
    
    dia_hoy = datetime.date.today()
    year = dia_hoy.year
    month = dia_hoy.month
    day = dia_hoy.day
    try:
        fecha_int = httptools.downloadpage(unmix(value99), timeout=2, alfa_s=True, ignore_response_code=True).json
        if fecha_int:
            fecha_int = fecha_int.get('currentDateTime', '')
            if len(fecha_int) >= 10:
                fecha_int = fecha_int[:10].split('-')
                if year != int(fecha_int[0]) or month < int(fecha_int[1])-1:
                    year = int(fecha_int[0])
                    month = int(fecha_int[1])
                    day = int(fecha_int[2])
    except:
        logger.error(traceback.format_exc())

    if init:
        updates = [(unmix(value7), unmix(val_1), init[0], init[1])]
        fecha_actual = "%s-%s-%s" % (year, month, 1)
    elif assistant:
        updates = [(unmix(value8), unmix(val_1), assistant[0], assistant[1])]
        fecha_actual = "%s-%s-%s" % (year, month, day)
    else:
        fecha_actual = "%s-%s-%s" % (year, month, day)
        channel_json = channeltools.get_channel_json(channel_name.lower())
        category = 'sys'
        if channel_json:
            if channel_json["adult"]:
                category = "adult"
            elif isinstance(channel_json.get("categories", []), list) and len(channel_json.get("categories", [])) > 0:
                category = channel_json.get("categories", [])[0].lower()
            elif len(channel_json.get("categories", '')) > 0:
                category = channel_json.get("categories", '').split(',')[0].lower()
            else:
                category = ''
            if category != "adult" and (category in ['movie', 'tvshow', 'direct'] or not category):
                category = item.contentType
                if item.contentType != 'movie':
                    category = 'tvshow'
            if "torrent" in category:
                category = 'torrent,'
                if item.contentType == 'movie':
                    category += 'movie'
                else:
                    category += 'tvshow'
        else:
            category = ''
            if item.server == 'torrent': category = 'torrent,'
            if item.contentType == 'movie':
                category += 'movie'
            elif item.contentType == 'episode':
                category += 'tvshow'
            else:
                category += 'sys'
        
        if item.sufix:
            sufix_out = '('
            for sufix in item.sufix:
                sufix_out += '%s/' % sufix
            else:
                sufix_out = '%s)' % sufix_out.rstrip('/')
                category += sufix_out
        
        server_category = ''
        if item.server == 'torrent':
            server_category = scrapertools.find_single_match(item.downloadFilename, '^\:(.*?)\:').lower()
            if not server_category: server_category = 'unkn'
        if "adult" in category:
            server_category = "adult"
        elif item.language:
            if server_category: server_category += ','
            langs = item.language
            if not isinstance(langs, list):
                langs = langs.split(',')
            if '*' not in langs[0].lower() and 'filt' not in langs[0].lower():
                if ('cast' in langs[0].lower() and 'vo' in langs[0].lower()) \
                            or ('lat' in langs[0].lower() and 'vo' in langs[0].lower()): 
                    langs[0] = 'dual'
                elif 'lat' in langs[0].lower(): langs[0] = 'lat'
                elif 'cast' in langs[0].lower(): langs[0] = 'cast'
                elif 'esp' in langs[0].lower(): langs[0] = 'cast'
                elif 'spa' in langs[0].lower(): langs[0] = 'cast'
                elif 'ita' in langs[0].lower(): langs[0] = 'ita'
                elif 'vose' in langs[0].lower(): langs[0] = 'vose'
                elif 'vos' in langs[0].lower(): langs[0] = 'vos'
                elif 'vo' in langs[0].lower(): langs[0] = 'vo'
                elif 'ing' in langs[0].lower(): langs[0] = 'vo'
                elif 'subt' in langs[0].lower() or 'vs' in langs[0].lower() \
                            or 'vc' in langs[0].lower() or 'vl' in langs[0].lower(): 
                    langs[0] = 'vos'
                if langs[0] not in ['cast', 'lat', 'vose', 'vos', 'vo', 'dual', 'ita']: langs[0] = 'otro'
                server_category += langs[0].lower()
        
        country = base64.b64decode(config.get_setting('proxy_zip')).decode('utf-8')
        country = scrapertools.find_single_match(country, 'Country:\s*(\w+)\s*\/')
        proxy_type = ''
        if channel_name == 'newpct1':
            proxy_channel = item.category.lower()
        else:
            proxy_channel = channel_name.lower()
        proxy = base64.b64decode(config.get_setting('proxy_channel_bloqued')).decode('utf-8')
        if proxy_channel in proxy:
            proxy_type = scrapertools.find_single_match(proxy, "%s[^']+':\s*'(\w+)[:|']" % proxy_channel)
            if proxy_type == 'ON':
                proxy_type = 'ProxyDirect'

        updates = [(unmix(value3), unmix(val_1), channel_name.lower(), category.lower()), 
                        (unmix(value5), unmix(val_1), country, proxy_type), 
                        (unmix(value6), unmix(val_1), item.server.lower(), server_category)]
    
    for value_t, val_u, value_f1, value_f2 in updates:
        sql_alfa = unmix(val_0) % (value_t, fecha_actual, value_f1, value_f2)
        try:
            cursor_alfa.execute(sql_alfa)
            result_a = cursor_alfa.fetchone()
        except:
            for line in sys.exc_info():
                logger.error("%s" % line)
        if result_a is None:
            sql_alfa = val_u % (value_t, fecha_actual, value_f1, value_f2, 1)
        else:
            sql_alfa = unmix(val_3) % (value_t, result_a[0])
        try:
            cursor_alfa.execute(sql_alfa)
            info_d.commit()
        except:
            for line in sys.exc_info():
                logger.error("%s" % line)
            info_d.rollback()
    
    info_d.close()


def unmix(val_x):
    unMixed = ''
    val_x = base64.b64decode(val_x)
    val_x = val_x[::-1]
    val_x = codecs.decode(val_x, "hex")
    if PY3 and isinstance(val_x, bytes):
        val_x = val_x.decode("utf8")
    for c in range(0, len(val_x), 2):
        unMixed += val_x[c]
    return unMixed


def failed_link(page_url):
    video_urls = list()
    try:
        base_url = unmix("MTRkMzk3NDc2NzA3ZjY5N2E1Mjc3MzM2NDRlNjk1NTYyNzYyNTYzNzU3NTI2NGQzMTNiNjc2ZTY3Njk2YTZjNjE2ZjM2NDA3MDU4NjE3MDc1NmUyNTYyMzgzNDZmNDU2NjcyNmM0ZDYyMzU2ODdmMjM1ZjY3Mzk2NjdlMjUzMjcxNzU2MjM5NzUzMTZiNmM2MjUwN2E3NTY5NzY3ODY5NjgzMjc3NDQ2OTY3NjQ2ZjI0NmYyZDZhMzA1Mzc5NjA3MzM0NzM3NDdjNjg2") % page_url
        session = requests.session()
        session.verify = True
        g_data = session.get("%sno" % base_url).content
        if PY3 and isinstance(g_data, bytes):
            g_data = "".join(chr(x) for x in g_data)
        packed = re.search(r"%s" % unmix("OTZlMzk3NDc2NzA3ZDY5NjM3MjdjNjM2MzczNzQ2ZjIxM2MzZjZmM2M0YTI4NmUyNjQ1NjE1YzI2NmI2MTRjMjQ2MzY1NWMyYzQxNjg0YzJhNTA3NDY4MmM2YzU0N2U2ZjZmNjI2OTZmNDQ3MjYzNjAzZTY2NDU3ZDY2NjI1ODI1M2M1NjRjNjM0MTY4NzY3NTY1NjE2OTIzNjM3ODc5NjIzZjNhNzgy"), g_data).group(0)
        unpackd = jsunpack.unpack(packed)
        unpackd = re.sub(r"\\'", "'", unpackd)
        unpackd = re.sub(r'\\\\x([a-f0-9]+)', lambda v: codecs.decode(v.group(1), "%s" % unmix("YTU4Nzc3NTZlNDg2")).decode('utf-8'), unpackd)
        cipher_data, js_code = unpackd.split(";")
        cipher_data = jsontools.load(re.search("%s" % unmix("ZjQ3Mjk1OTIwM2IyOTdkNTYzNzI1NmU1NjdiNTg2ODI2NDcyODNkM2Y2MTY2NzQ3NzcxNjI3NDYyNTAyOTQyN2E2MTY4NTY3"), cipher_data).group(1))
        so_json = decsojson4(js_code)
        pwd = re.search(r'%s' % unmix("NjUyMjA3OTI2NGIyNzZkNTU1MjI4N2U1MDdiNTU0ODJhNzIyMjYwMjA1ZDM3NjAyODUzNzM1Mzc3NDE2ODYwNw=="), so_json).group(1)
        sourcs = get_sources(cipher_data, pwd)
        listed = []
        for v_data in sourcs:
            j_data = jsontools.load(v_data)
            g_url = "https:%s" % j_data[unmix("ODY1NjQ1YzYxNjk2MTY2Ng==")].replace("\\", "")
            if unmix("MjdjNjc0MTYwNWU2ODc5NjY1NzY4Mzk2NjYyNzE0ZjY=") in j_data[unmix("NDdjNjE2NTY0MzI2YTcxNmY0YzY=")].lower():
                j_data[unmix("NDdjNjE2NTY0MzI2YTcxNmY0YzY=")] = ""
            if j_data[unmix("NDdjNjE2NTY0MzI2YTcxNmY0YzY=")].lower() not in [unmix("NjU0NzI1YzY2NjU3NDYxNjA1NjZhNDU2NTY0Ng=="), unmix("YTc1NmU2NDc4N2M2NjY1N2Q0MTYzNTY2ODM1Njg3NDY=")] and not j_data[unmix("ODY1NjQ1YzYxNjk2MTY2Ng==")] in listed:
                if "%s" % unmix("MjdjNjc0MTYwNWU2ODc5NjY1NzY4Mzk2NjYyNzE0ZjY=") in j_data[unmix("NDdjNjE2NTY0MzI2YTcxNmY0YzY=")].lower():
                    j_data[unmix("NDdjNjE2NTY0MzI2YTcxNmY0YzY=")] = ""
                if not g_url.endswith(unmix("ZDQ4MzU0NTdkNjMzMTRkNg==")):
                    g_session = requests.session()
                    g_session.verify = True
                    g_headers = {unmix("OTM1NjA3NzY2M2U2YTcxNjAzMjc="): unmix("MTNkMjY0MDMxNWQzMzQzNzk3NTZhNjQ3YTQ5NzkzMjY="), unmix("NjQ0NzY0ZTY2NzU2YTQ3NjY3MTY3NmQyOTcyNzU3NTYzNDM3YTc1Nw=="): "%s" % UA}
                    t_session = g_session.get(g_url, headers=g_headers, allow_redirects=False)
                    u0 = t_session.headers[unmix("NjZlNjg3ZjYzMzk2NTY0NzM2MTY3MzM2MTNmNjc2YzY=")]
                    x = 0
                    while unmix("NjZlNjg3ZjYzMzk2NTY0NzM2MTY3MzM2MTNmNjc2YzY=") in t_session.headers and x < 20:
                        x += 1
                        t_session = g_session.get(u0, headers=g_headers, allow_redirects=False, stream=True, timeout=5)
                        if t_session.status_code in [200, 206]:
                            break
                        u0 = t_session.headers[unmix("NjZlNjg3ZjYzMzk2NTY0NzM2MTY3MzM2MTNmNjc2YzY=")]
                    if t_session.status_code == 206:
                        g_ck = urllib.urlencode(g_session.cookies.get_dict())
                        g_url = u0 + unmix("NTMzNzc2NTI2NWQzMTM1NjM2OTY4NmI2ODdmNjM0ZjYzNjM0MzZjNw==") % g_ck  + unmix("MTczNzQ1NTJkNmQzOTc0NzU3ZTY3MzU2NTU3NjY1MTQxM2QyOTYyNzMzNTY2NTM3Mjc1NTI0NjI=") % UA
                    else:
                        g_url = u0 + unmix("MzMzNzI3NTJiNGQzODQ0Nzg3ZTYyNTU2MDM3NjM0MTQxM2QyODYyNzk2NTY4NjM3OTQ1NTg1Yzc=") % UA
                else:
                    if unmix("NTczNzY3YzY4Njg2NDMwMjk1ZjY4NWU2") in requests.get(g_url).text.lower():
                        continue
                video_urls.append([".%s %s" % (j_data[unmix("YTc1NmI0MDc1NTk3MDc0Nw==")], j_data[unmix("NDdjNjE2NTY0MzI2YTcxNmY0YzY=")]), g_url])
            listed.append(j_data[unmix("ODY1NjQ1YzYxNjk2MTY2Ng==")])
    except:
        pass
    return video_urls


def decsojson4(so_data):
    if not so_data.startswith(unmix("YTZkNWE1NzI3MzQzZjQ2Nzc2ZTI4NGU2MzRmNjQzMzcxM2E2NTZmNjM1MzczMzcyMTNiNQ==")):
        return unmix("NzRmNjUzNDZiNDk2YTRjNmQ2MTZlNjY3NzMwMjIzMzc5NzU2MjMwMjk0ZjZkNGU2MTQwMjUzZjY0NDc2NDM5NjM0NDZkNmY2NjczNjk3MDIzM2M2YTc1NA==")
    j_args = re.split(r"[a-zA-Z]", so_data[222: len(so_data) - 58])

    decoded = "".join([chr(int(so_x)) for so_x in list(j_args)])
    return decoded


def get_sources(src_data, passphrase):
    encrypted_text = src_data[unmix("MjM0NzQ3MzY=")]
    encryptd_text_bytes = base64.b64decode(encrypted_text)
    g_salt = codecs.decode(src_data[unmix("ODQzNw==")], unmix("MjQ4N2Q2NTZmNjg2"))
    encryptd_text_bytes = encryptd_text_bytes[16:]
    g_resp = jscrypto.evpKDF(passphrase, g_salt, key_size=12)
    g_key = g_resp.get(unmix("YzY5N2M0NTZhN2I2"))
    g_iv = g_resp.get(unmix("MTU2NzEzOTY="))
    g_key = g_key[:len(g_key)-16]
    g_aes = jscrypto.new(g_key, jscrypto.MODE_CBC, g_iv)
    decrypted_text = g_aes.decrypt(encryptd_text_bytes)
    encoder = jscrypto.PKCS7Encoder()
    unpad_text = encoder.decode(decrypted_text)
    unpad_text = codecs.encode(unmix("ODc1NzczNjZhN2QzODY1NmE1Yjc4MzkyNjc0NjkzYzIwMzU2ZjRjMmM0YjY5M2MyMDUzNmU2YzI2NjE2NjdjMjMzMDdhNDgyMTNlNmM2ZjZhNzk2ZDQ0NzU2MzY5M2U2ZTQ1N2Y0NjY2NDgy"), "utf-8") + unpad_text[16:]
    js_dec = codecs.decode(jsunpack.unpack(unpad_text), unmix("OTQ1NmI0MDcxNzE2YTczNjYzMzc2NDU2NjZmNWQ0NTZhNDQ2ODNmNmE2MzZkNjk2MTVlNmY0NTc="))
    sourcs = re.compile(r'%s' % unmix("MzM5Mjk3ZDcwN2YzNzdhMmU0ZTJkNGYzMzNjMjA1MjI5NWIyZjRkNTYzMjJlNGU1MjNiNTA3MjJhNWEzOTQyMjQ0NTY5NzA3NjQ5Nzg3NDcyNjIyZDZjMjU3MjJmNmIyNTNkNTg3MjIyNWU1OTNiNTI3MjI2NmEzMzUyMjI3YzY1MzU2NzUyNjY0MTY5N2M2MzYyMjE3YzI5NDIyYTdiMjQ1ZDViNjIyNjVlNTczYjU1MzIyNTZhMzc1MjJkNjU2OTZjNmQ2OTY4NzY2MTQyMjk1Yjc5Mzgy"), re.DOTALL).findall(js_dec)
    return sourcs


def jhexdecode(var_te):
    chinga = unmix(
        "NzVkN2M0ZDc4NTIyNzYzNzY0NTIxM2YyMTYzNjU1MzY3NWUyOTM0NjQ1MTYyNGY2YjRjNjY0MDcyNjU3NzZlNmQ2YjZiNDM2NDY5NjE3YzYyNjM2NzdmMjY0ZjI3NGEzNzUzNzA1MDdlNjQ3MDM0NzYzODY5NzIyZTQwMmI2YTM0NDIyMjQ0Njc0MjJiNDAyMzVjMjY2MjJjNjQ2NjUyMjEzMDI2NGEzMTYyMjg2NDdiNDIyZDRiN2M2MDI4N2EzYzYyMjEzODM3NzMzMjYyMjU1MDI4NWMyODVkNzM3MjI5MzM3MjM1Mjc1ZjI5NmQ2NDZmNjU3MzZiNmUyNjM4NzE1ZjZiNDI2NjZmNjc1NDdkNjA3YTY1N2U0ZjI5NWYyMDdhMzU1Mzc2NjA3NjM0NzczNDc5Nzg2NDUyMjM2MDIyN2EzMzcyMjI1NDY1MzIyNjYwMjg3YzIyNTIyNDQ0NjY3MjJiNDAyYTdhMzQ3MjI3MzQ3NDQyMjM1YjcyNjAyYTRhMzA3MjI0MzUzMzYzM2E0MjJhNjAyNjRjMjI1ZDc3NzIyZDRjNjAzZDYzNjQ3NTc4NjQzZTJhNDM3OTY1Mjg3ZDI1NDQ2ODc1Njk0MjY5M2Q2MTU1NmE3ZjIyNjQ3NDY1NjYzZTYzNGUyODQxNjA3YTc1M2Y2Nzc0NjEzOTY0NjY3NDNmMjg1ZjIyNGEzZjYzN2U0MDcwNTQ3ZTY0NzUzODY3MzIyMTMwMjg3YTNlNjIyMTU0NjYzMjJkNjAyOTVjMjI3MjIzMzM3NzMyMjY2MDIxNWEzYTcyMjUzNDcyNjIyZjZiN2Y0MDI4NGEzODQyMjE3MTM0NTMzOTYyMjQ2MDI4NGMyMjRkNzg2MjI5NzM3Mzc1MjY0ZjJkNmQ2MDNmNjEzMzY3NWUyNzM1NmE3Mjc3MzE2MTNjNjgzNjYwM2Y2MDMyNzUzNDc3Nzk2YzZlNjk2ZjIyM2YyZjRhM2M0MDc2NzQ3Njc0NzczODYxMzIyMTUwMmE2YTMzNTIyMzU0Njc1MjJiNjAyNDVjMjc3MjI5NjQ2MzUyMmM0MDI2NGEzNzQyMjk0NDdiNDIyODNiNzk0MDIwNWEzYzYyMjA1NzM4MzIzYTcyMjkzMDI5NGMyZjZkNzI3MjI3NjM3ODQ1MjMzZjJkNGQ2MDNmNmU2MzZhNGUyNTc1Njc3YzY1Njk2ZDY2NmE2NDc3MzE2NTNiNjU3ZjI2NmYyNzdhM2E0MzcyMzA3NzU0NzM2NDcyNjg2MDUyMjI2MDJhNWEzOTMyMjIzNDYzNDIyNDMwMjI1YzI5NjIyYzY0Njk3MjIyMzAyNzNhMzY3MjI0MzQ3NTcyMjczYjdjNjAyMjdhM2U2MjIzNDQzMTMyMzk0MjI4NDAyNjVjMmU0ZDczNzIyNDUzNzQ0NTI1NGYzNDVmMmI0ZDY1NGY2MzMzNmM2ZTJhNTI3NTQ1NjI1OTYyNjg2ODYzNjE1OTY5NzY2MTQxM2I0ZjI5N2YyNTVhM2U2Mzc1NjA3OTU0NzE3NDdjNDg2YTcyMjY1MDIyNmEzZTQyMjM0NDYxNjIyMDcwMjg0YzI4NjIyNzM0NmU2MjI5NzAyNjRhMzM1MjJhNTQ3NDUyMmM2YjdmNjAyYTdhMzU0MjI3NjMzNjMyMzQ1MjI3NDAyNzVjMmM2ZDcyNjIyYjQzN2U2NTI3NGYyOTY4NjQ2MzcwM2UyNDcxNjk2ODcyMzU2MzdkNjgzZjI1NmYyNTZhMzgzMzdhNTA3ODc0NzA1NDc2NDg2OTMyMjE1MDI0NmEzMzQyMjk1NDYyNjIyMDUwMjU1YzIzNDIyNjM0NmY0MjIzNDAyMzRhM2M2MjJjNjQ3NjYyMmE0Yjc2NTAyMzNhMzE1MjIzNDIzMzcyMzczMjI4NDAyMTNjMjE3ZDc2NTIyMjdjNmI0ZDZlNDQ3MTQ4Njg2ZTI0NzM3YTQ1MjYzZDI4NTQ2OTc1Njc3MjZkNGQ2NDQ1NjM0ZjI2NmY2NjQzNmE1ZTI0NmU2NDc5Njc0MjY2N2Y2ODc1NjQ0NDY2NTk2Njc2N2E2ZjI4N2YyMDNhM2Q2Mzc0NTA3NTM0NzM0NDc3NTg2YjQyMjk0MDJiNGEzYTUyMjE0NDYxNDIyMTMwMmQ2YzIyNzIyNTQzNzY3MjI0NDAyZjRhMzk2MjI5NzQ3NDMyMjA1Yjc0MzAyNDRhMzg0MjI2NDYzMzUxMzI1MjIzNTAyOTdjMjA3ZDc0NDIyYTUzNzU1NTJlNmYyMjM1NjI0ZjI2NGY2ODYzNmE3ZTJlNjA3MjZmNmI0Mjc0NzQ2ZjY4N2I0OTY2N2Q2NDdmMjczZjI5NGEzMDMzN2M0MDczNzQ3NDM0NzU2ODY0MzIyOTYwMjk2YTNlNjIyYTc0NmU0MjJlNDAyMTdjMjI0MjJkNDM3YTQyMjE2MDIzNWEzMzUyMjU3NDc3NDIyMTRiNzI3MDI3NWEzYTYyMmE2NTMwNzEzNTQyMjYzMDIyNWMyNjdkN2M0MjI4N2M2NDNkNjEzNDc1NDg2MjdlMjY2MzczNTUyMDVkMmU0NDY4NDU2OTQyNjc0ZDZhNTU2NTZmMjk1NTZmNGQ2OTdlMjczODc4NWY2MzdjNjY2NDY3NDk2MjY2NzU0ZjI1N2YyNjZhMzE0MzcwNTA3MzY0NzI0NDc0NTg2MDUyMjc3MDJiNGEzOTcyMjQ1NDYwMzIyZDQwMjE3YzJmNDIyMzMzNzM1MjI5NjAyNzVhM2Y2MjIzNTQ3OTMyMmE3YjdhNjAyMzNhM2I2MjI5NzQzNjYxM2M0MjI3NTAyNTdjMjg1ZDcxNzIyNzVjNjk2ZDY4NTQ3YTU4NmY2ZTI5MzM3ZTQ1MjU3ZDI5NDQ2OTU1Njg3MjZhN2Q2NTM1Njk1ZjIzNWQ2YjZmNjA3MzY3NWUyODZmNjI0NTY4MzQ2NjU5NjI2Njc5NGY2MjdkNjE3MTYzNjc2YjRmMjY3ZjIwM2EzNDMwNzIzNDc1NjQ3ZjQ4NmY0MjI1NDAyOTRhMzY2MjJiNjQ2MDUyMjA3MDIxNGMyNjYyMjU1MzcxNTIyYTcwMjM3YTMyNjIyYjQ0NzU3MjIyN2I3YzQwMmE0YTM5MzIyMzQyMzc0MTM1NTIyOTYwMmI2YzIzNmQ3MzQyMjI1YzY3M2Q2NTQ0NzI1ODY4N2UyMjUzNzM0NTIzM2YyNzY1NjIzYzZhNjk2NzU2NjQzZjIzNzQ3ZDQ1NjIzZTZhN2UyMjcyNzQzZjY5NjQ3OTUxNmM2NzYwMzQ2MjU5NjE0MDc3NzE2YzQyN2Q0ZjIxNGYyZTRhMzY0MzdlNDA3NDc0Nzk2NDdlNDg2NzYyMmE1MDI1M2EzNzYyMjI0NDZlNjIyMTUwMjk1YzI2NDIyNTY0NjE2MjJkNDAyODNhMzU1MjI5NzQ3OTcyMmQ0YjcwNTAyZTRhMzMzMjIxNTAzYzQxMzI0MjIxMzAyMTRjMmE1ZDc3NzIyZjYzN2E0NTI3NWYyMjY2NjQ3ZjI5NzQ3NTU1NjU3ZTZlNGUyYTU0NjkzNTY3NDQ2MjUxNjk1ZjYzNmM2OTYwNzEzNTc2NmYyMjNmMmQ0YTNlNDA3ZTY0NzQ2NDc5NDg2MzUyMjk1MDI0M2EzMzQyMjM3NDY0NDIyNTYwMjAzYzJmNDIyYTY0NmY0MjI1NzAyNzNhMzc2MjI3NjQ3NjcyMjg3Yjc4NzAyMTZhMzU3MjIxNDkzMjcyMjU0MDI3NWMyZDRkNzQ0MjI0NzM3ZjY1Mjk2ZjIyMzU2OTVjNjIzOTZjNDY2NzdmMmM0ZDYwNWY2YjYzNjI0ZTI4NDk3YTQyNzU2ZjY4NzQ3ODMzNjc3MTZlNDY2OTc1NjE1YzYxNzk2YTQ2NjEzZTI4NDc3NDQ3NzM1NzczM2YyMzdmMmM0YTM3MzA3NTU0NzY2NDcxNzg2ZDYyMjg1MDI1N2EzMjQyMjY1NDY5NTIyYTcwMjc2YzJjNDIyZTQ0NjQ3MjI2NzAyNzVhM2I0MjI2NTQ3NDYyMjA3YjcxNDAyMDVhMzk1MjI4MzgzNDYyMjg1MDI0M2MyNDZkN2E1MjI0NDM3ODc1MmQ2ZjI2NjU2MDdmMjY0ZDY4N2Y2NzUzNjg3ZTI0NTU2NjUwNzY1MTY2NTQ3ODRkNjg3MTY5NzU2ODcyNzc3NDc5NTM3YjRmMmM0ZjI0NGEzOTYzNzY1MDc2NDQ3NTM0N2E2ODZlNjIyMjMwMjI1YTM2NTIyNzY0Njg1MjIxNzAyOTRjMjg2MjI0NDM3NzcyMjQ3MDIwN2EzNjcyMmE3NDcwMzIyOTViNzI2MDIxM2EzNDMyMmM0NjMzNjIyYTYwMjY0YzI4NGQ3MDcyMjc0YzZiNGQ2NzY0N2E3ODY4NGUyYTczNzE1NTI2NmQyMDM0NjEzNTZmNDI2MDVkNjc0NTY1NWYyNzU2NzkzNDdmNmUyZjRmNjQ3NTZhNjQ2MzQ5NmI0Njc4NTQ2ODM1NzIzZjZkNGM2MDczNjE3ZjI1NmYyNjZhM2M2MzcyMzA3YzY0N2E1NDc2Nzg2NzUyMjM0MDJlNmEzYTUyMmI0NDZmNjIyMDMwMjY2YzIzNDIyMzMzNzE2MjI5NDAyMzVhMzM0MjI1NzQ3NTMyMmQ2Yjc1NjAyMDNhMzk0MjJhNTUzMzQyMmE1MDJhN2MyZDRkN2Q0MjI3N2M2YTRkNjU1NDcxNDg2ZjRlMjE0MzdjNDUyOTdkMjg1NDYzNTU2ZTYyNjI2ZDY0MzU2NjdmMjk0ZjYyNzQ3ODVlMjg3ZDY4NjE2NDY1Njk2Mjc5MzQ3MTczNzQ2MDczMzU3NDVmMjE0ZjJhNWEzODQzNzIzMDdhNDQ3YjY0N2U0ODYxNDIyZjQwMjY1YTM2MzIyNDU0Njg1MjIzNjAyMzZjMjM2MjIxNDM3ZDYyMjgzMDIyN2EzYjQyMmM2NDc3NDIyNTdiNzE3MDIyNWEzZjQyMjE0NDMyMzIyYzRiNw==")
    return eval(chinga)

    # var_te = var_te.replace("'", '"')
    # var_erre = re.sub(r'_\d+x\w+x(\d+)', 'var_' + r'\1', var_te)
    # var_erre = re.sub(r'_\d+x\w+', 'var_0', var_erre)
    # def to_hx(var_ce):
    #     var_ache = int("%s" % var_ce.groups(0), 16)
    #     if 19 < var_ache < 160:
    #         return chr(var_ache)
    #     else:
    #         return ""
    # var_erre = re.sub(r'(?:\\|)x(\w{2})', to_hx, var_erre).replace('var ', '')
    #
    # var_efe = eval(re.search(r'%s' % unmix("MjViMzU1OTI0NGIyMzRkNTk1YjM0N2U1MDViNTczODJiNGEyYzQzN2Y2YzU0NWQzNDRhMjIzMzc2NmM1MzYwMzIzZjUyNzI3MjMxNjQ3Njc2NGEyNTUzNzE0YzU="), var_erre).group(1))
    # for var_ind, var_val in enumerate(var_efe):
    #     var_erre = var_erre.replace('[[var_0[%s]]' % var_ind, "." + var_efe[var_ind])
    #     var_erre = var_erre.replace(':var_0[%s]' % var_ind, ":\"" + var_efe[var_ind] + "\"")
    #     var_erre = var_erre.replace(' var_0[%s]' % var_ind, " \"" + var_efe[var_ind] + "\"")
    #     var_erre = var_erre.replace('(var_0[%s]' % var_ind, "(\"" + var_efe[var_ind] + "\"")
    #     var_erre = var_erre.replace('[var_0[%s]]' % var_ind, "." + var_efe[var_ind])
    #     if var_val == "": var_erre = var_erre.replace('var_0[%s]' % var_ind, '""')
    # var_erre = re.sub(r':(function.*?\})', r":'\g<1>'", var_erre)
    # var_erre = re.sub(r':(var[^,]+),', r":'\g<1>',", var_erre)
    # return var_erre

def obfs(obfs_data, obfs_jsCode):
    obfs_ene = 126
    obfs_data = re.search(r'%s' % unmix("MzQ3MjkzOTJjNmIyYTRkNTM1NzIyNGU1MzViNTM3ODI0NjcyMzRhMjY0MzcyNWM1ODdkMzI1YTIwNzM3NjNjNWE3NDYzMzE2YzYwMjY2Mjc3NjE2ODM2Nw=="), obfs_data).group(1)
    try:
        obfs_keY = re.search(r'%s' % unmix("Mzc5Mjg2YzUyNzkyMzdiMmE0NzdhNWM1ODc4Nzk2MDNlNjgyZDQ4MjY1YzVmNmYzMjRhMjAzZTIyMzI2ODNmNjAzNDczNTE2ODM4MjU0YzU="), obfs_jsCode).group(1)
    except:
        if obfs_data[:2] == unmix("MzcxNTc3MTY="):
            obfs_keY = unmix("MjQ0MzI1MTM=")
        else:
            obfs_keY = unmix("NzU1MzIzMTM=")

    obfs_keY  = obfs_ene - eval(obfs_keY)
    obfs_data = base64.b64decode(obfs_data)

    if PY3: obfs_data = "".join(chr(var_equis) for var_equis in bytes(obfs_data))
    var_chars = list(obfs_data)
    for var_ii in range(0, len(var_chars)):
        var_ce = ord(var_chars[var_ii])
        if var_ce <= obfs_ene:
            var_number = (ord(var_chars[var_ii]) + obfs_keY) % obfs_ene
            var_chars[var_ii] = chr(var_number)
    return "".join(var_chars)




def identifying_links(js_data):
    from core import scrapertools
    
    b = 0; c = 0; d = 0; e = list(); f = list(); k = list();
    js_data = scrapertools.find_single_match(js_data, r"join\(''\);\}\((.*?)\)")
    
    list1, list2, list3 = scrapertools.find_multiple_matches(js_data, r"'(\w+)',")

    while True:
        if (b < 5): f.append(list(list1)[b])
        elif (b < len(list1)): e.append(list(list1)[b])
        b += 1
        if (c < 5): f.append(list(list2)[c])
        elif (c < len(list2)): e.append(list(list2)[c])
        c += 1
        if (d < 5): f.append(list(list3)[d]);
        elif (d < len(list3)): e.append(list(list3)[d]);
        d += 1
        if (len(list1+ list2 + list3) == len(e + f)): 
            break
    a = ''; b = 0; c = 0;
    h = ('').join(f)
    g = ('').join(e)
    
    while (b < len(e)):
        l = -1
        if (ord(h[c]) % 2): l = 1
        k.append(chr(int(g[b:b+2], 36) - l))
        b += 2
        c += 1
        if(c >= len(f)): c = 0
    
    a = ('').join(k)
    
    return a


def gvd_check(page_url):

    data = httptools.downloadpage(page_url, alfa_s=True).data
    vid = yev(data)
    if not vid:
        video_id = scrapertools.find_single_match(page_url, 'v=(.*)')
        uuu = unmix("ZjQ4MzE2NzUxMzM2ZjYxN2M2MTM4NTEzMTVmNTIzOTMzNjk1NzNmNTI2NzcxNWM2NjM5NjI2MzQxNjc0NjVjNGM0ODRhNDU0OTQ0NTQ1MzU2NTQzOTQxNTM2ODM1NzU1ZTYxNzE2YzYyNDM1MTcyMzE2YTRmNjY0NjRmNTM2ZjQxNjE0Mzc5NzM3MzVhNzE2MTNhNzIzOTQxNzE0MTZkMzIzOTc5NTU2ZTRiNjY1ZjM4NjI3ODU1NmE2OTdlNjE2ZTZjNjE3MDc3M2YyNjcxMzEzNjcyNGYyMDc5NjkzNTZlNjI2OTU1NzQ1NDc5NjU3MjVmNjY1OTc5N2YyMjdkNjg0ZjYxNDM2YTdlMjU2NTYzNDI2ZjQ1N2Q2NDdjNDU3OTZmNjk2OTczNmUyNzc3NzIzNzc1Mzc3NTRmMmE1ZjJiNGEzYTczNzc2MDcwNTQ3ZTQ0NzM3ODY=")
        post = unmix('MjZkNzE1MjIzMzM3YzQ1MjYzMjI2NGEzOTMyMjI3NDY5NDk0NzRmNjgzNTY0NjQ2ODM5NjUzNjc4NzIyNDVjMmQ2ZDc3NWQ3MDcyMjgzZDYyNGY2NTYzNjM2ZTI2MzU2NjYyNmE0NTc5NzQ3ODY1Nzg0ZjY0Nzk3NDVlMjE0NzdhNjc3ZTQ3NzY3ZjI4NWYyOTNhM2E1Mzc3NzA3NTY0NzM1NDc4Njg2ZDYyMjg3YTM5NjIyODNjNjQ2Mjc2MzU1NDY0NjA3NTZmNDI2NTdkNjg1NTYzNjIyOTZiNzE3YTNkNjIyNTQ5NzE1NDc1NTI3ZjQxNjMzMDU0NjQ2ZjQyN2Q0OTY5NDg2MjU0NzMzMjI3NWMyZjRkN2E3MjI4NTUzNjYwMzU2ZTI1NzYzNjMxMzg0MjIyM2EzNzQyMjQ3ZTYxNGY2NTc5NjI0MzdjNjI3ODM1NjY3NjU0MzQ3MzdlNjczNTY0NTk2YzRjNjE1MzZlNjIyMzdjMjc2MjIxNzQ0OTc1NDM3MjQ0M2Q0MzY1NDA3MjI2M2EzODMyMmI2ZTYyMzU2MjU1NjE0Mjc4NTM2YTczNWY2NDc2NWU2MDU1NjU0OTY4N2M2MTMzNjc0MjI0NGMyYTQyMjEzNDQ3Nzk0MTRmNDg1MjViNjQ0NTdlNDQ2MTQ3NDIyMTdhM2E2MjI4NDU2MDdkNmI0MTZlNmU0NTM0NzY2ZTYyNTU2OTU5NjMzYzY4MzM2YjYyMmE2YjcyNWEzNjcyMjI3NDdmNmU2YjQ1Njk1OTY2NWM2OTMzNjc3MjI5NGI3ZDRhM2M0MjIwMzQ3MDc4NzQ3NTZkNDQ3MjNlNmQ0ZjY3MzM2OTYyMjY1Yjc=') % video_id
        data = httptools.downloadpage(uuu, post=post, alfa_s=True).data
        vid = yev(data)
    if vid:
        return vid


def yev(data):
    vid = list()
    bloque = scrapertools.find_single_match(data, '(?is)"formats":\s*(\[.*?\])')
    if not bloque: return vid
    opt = json.loads(bloque)
    for jj in opt:
        itag = jj.get("itag","")
        quality = jj.get("qualityLabel", "").replace("s", "p")
        video = jj.get("url", "")
        if video:
            vid.append(["%s" %(quality), video])
    return vid


def get_hl_data(page_url):

    master_url = "https://highload.to/assets/js/master.js"
    master_result = get_result(master_url, page_url)
    var_value = scrapertools.find_single_match(master_result, "var res\s?=\s?([^.]+)")

    result = get_result(page_url)
    try:
        sub_url = scrapertools.find_single_match(result, 'suburl:"([^"]+)"')
        title = scrapertools.find_single_match(result, 'title:"([^"]+)"')
        sub = "%s%s" % (sub_url, title)
    except:
        sub = ""
    value = scrapertools.find_single_match(result, '%s\s?=\s?"([^"]+)"' % var_value)
    res = scrapertools.find_single_match(master_result, 'var res\s?=\s?%s.replace\("([^"]+)"' % var_value)
    res2 = scrapertools.find_single_match(master_result, 'var res2\s?=\s?res.replace\("([^"]+)"')
    value = value.replace(res, "")
    value = value.replace(res2, "")
    media_url = base64.b64decode(value).decode('utf-8')
    return media_url, sub


def get_result(url, ref=None):

    data = httptools.downloadpage(url, headers={"referer": ref}, alfa_s=True).data
    if PY3 and isinstance(data, bytes):
        data = "".join(chr(x) for x in bytes(data)) 

    if ref:
        script = '(var _0xc\d+e=.*)'
    else:
        script = '<script type="text/javascript">(var _0xc\d+e=.*?)</script>'

    code = scrapertools.find_single_match(data, script)
    start = r'decodeURIComponent\(escape\(r\)\)\}\(\"'
    end = r'\)\)'
    pattern = r'(.*?)'
    code = scrapertools.find_single_match(code, start + pattern + end)
    code_list = code.split(',')
    for idx, code in enumerate(code_list):
        if code.isdigit():
            code_list[idx] = int(code)
        else:
            code_list[idx] = code.replace('\"', '')

    result = panter(*code_list)

    return result


def duf(d, e, f):
    values = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/"
    g = list(values)
    h = g[0:e]
    i = g[0:f]
    d = list(d)[::-1]
    j = 0
    for c, b in enumerate(d):
        if b in h:
            j = j + h.index(b) * e ** c

    k = ""
    while j > 0:
        k = i[j % f] + k
        j = (j - (j % f))//f

    return int(k) or 0


def panter(p, a, n, t, e, r):
    r = ""
    i = 0
    while i < len(p):
        j = 0
        s = ""
        while p[i] is not n[e]:
            s = ''.join([s, p[i]])
            i = i + 1

        while j < len(n):
            s = s.replace(n[j], str(j))
            j = j + 1

        r = ''.join([r, ''.join(map(chr, [duf(s, e, 10) - t]))])
        i = i + 1

    return r


def get_ssb_data(page_url):
    video_urls = list()
    from lib.generictools import rec

    page_url = page_url.replace("/play/", "/d/")
    _id = scrapertools.find_single_match(page_url, r'/d/(\w{12})')

    new_data = httptools.downloadpage(page_url, alfa_s=True).data
    pattern = unmix('MTdlMzkzNDY5MzQ3MTZmMjE3YzMxNWYzOTRhMjk3ZTI1NWMyMTM5MjY1YjIzNTQ2YjZjNTA3ODI1Nzg3MTViMjQ0NDY0NGM1MTZlMzc1NDY3NTQ3MjNjMzE0ZTNmNjQ2ZTY0NzU0ZjIxNGMzNDRlMzA1MTY0M2YyMTdjM2Q2ZjMxNGEyNTRlMjc1ZTNkNDIyNTU5Mjc0YzUzNDcyODM5MjQ2YjI5NmQ1MTY3MjAzZTVlNmI1ZDQ4MjU3NzIyNmMyNzU3MjQ3OTJhNmIyMzNkNTc0NzJmNmU1MDViNTI1ODI5NTcyZDZjMjY3NzI5NDkyNjNiMjMzZDUyNjcyMTVlNTM1YjUxNzgyOTU3MmY2ODI0NWM1OTNmNjI3NTY2NTQ2MDU5NmY0Njc3M2Y1MTM0Njk3MTZhNWY2MTNjNjI3ZTYzNjc3NDdmNjY1NDYwNTIyOTdkMzE1YjY3MzM2ODY5NjA3YzYzNTM2NzZlNmU0ZjY=')
    matches = re.compile(pattern, re.DOTALL).findall(new_data)

    for v_id, value, hash, qlty in matches:
        base_url = unmix("OTUzNzg2NTI4N2QzNDc4NmI2Mzc5NzE2NTM4NmE2NjIyNzM3Nzc1MmQ2ZDMxNDU2NDY0NjQ2ZjY1M2Q2ODM2Mjk2Mzc2NTUyODNkMzM3NDY5Mzk2MTM2MjE1NzY0NDk2OTQyNzE0ZjY3NGY1YzY0NjM3MTY3NmY2ZTRjNjUzZTY0Nzc3MzZmNjIzNDY5M2QzZTYwNzI2ZjY1N2YzOTdjNjI2NDZhN2YyMDc0N2E0NTY2NWU2ZjZlMjI2MjYzMzM3NDZkNjk2MTZhNTU2NzcyNzYzNDc5NjM3NDdmMjE3ZjJiNmEzYTQzNzc1MDdmNDQ3Mzc0N2E2ODY=") % (v_id, value, hash)
        new_data = httptools.downloadpage(base_url, alfa_s=True).data
        key = scrapertools.find_single_match(new_data, 'data-sitekey="([^"]+)"')
        co = "aHR0cHM6Ly9zdHJlYW1zYi5uZXQ6NDQz"
        loc = "https://streamsb.net"
        tk = rec(key, co, "", loc)
        new_data = httptools.downloadpage(base_url + "&g-recaptcha-response=%s" % tk, alfa_s=True).data
        video_url = scrapertools.find_single_match(new_data, unmix('NjNlMzc1MTY1N2YyMjdjMzc2YjY0NmU2ODY5Njc3YzQzNTAyODU0Njk2MTY3M2Y2NjZjNjY2ZTY4NDc3MzRmNmY0NDQ5NjAyMjU0NzE2MzZkNDU2MjYyNzQ2OTY0NDQ0MTVlM2E3MjI4NjkyMTRiMjk1ZDU4NTIyNDRlNTc3YjUwMzgyNjUyMjE0ZDNjNDY2ZTQ1NjQ3Mjc3Nzg2MTcwMjQzMTZlNmMz'))
        extension = scrapertools.get_filename_from_url(video_url)[-4:]
        sub = ""
        if not extension:
            continue
        video_urls.append(["%s %s [StreamSB]" % (extension, qlty), video_url, 0, sub])
    video_urls.sort(key=lambda item: int(re.sub("\D", "", item[0])))

    _id = codecs.encode(_id.encode(), "hex").decode()
    url = unmix('NjUyMzczNjMzMzMzMjM3MzY1NDYxNjYzYTYxMzQ0NjMyNTUzMTM2MzE3MjMxNTczMzM0Mzg0NzM5NjMzMzM3Mzk0MzYxNTczNDUzNjg3NzNlNDE2MzY2MzE0NjY5NzYzYzYwMzUzMzM3MzE2MzY3Mzg1ODM5NTQzMDM5MzQ3NzMzNDIzZjY1M2Q2MjM0NTQzMTU0Mzg2NjNhNzYzMzU2M2E2MTYxNjUzNDQ0Njk2NDMyNTM2MTc3M2Y2MzY3NjczYzQyMzc1MzMyNTYzYjQzMzk3MzM4NDMzMTU3Mzc1MzM0NzQzMjM2MzM1NjM2NDMzMTMxMzQ2MzM3NjYzMDMzMzk0NTM3MzMzMDM2MzM2MzM1NTIzNjMzMzc2NzM2NjMzMjQ0MzM1MzM0NDczMjMzMzg0MzM4NDMzZTQ3MzM1MzMyNDMzNDM2M2M0NzNhNTMzNDYzMzY3NjMxNzczZDYzMzE0NDMyNTMzNzc2MzU1MzMyMzQzOTY2MzY3NDM1MzMzYTQ2MzM2MzNmNDczMDMzMzYzMjNjNjMzMTUzMzk0MzM5NTczZDQzM2M0NTNmNjMzNDQ0MzQ2MzM4MzYzMzMzMzgzNTNhNjMzYTU0M2U0MzM2NzMzYTQ2M2Q0NDM3NTMzNjcyM2M2MzNmNDYzZjQzM2M2MjMzMzMzZDQ2M2E3MzMxNjQzYjQzM2Y2MzM0NjMzNTY5MzU0MzM1NjYzYTUzMzQzMzM0NjYzMzc3MzUzMzMxNzMzNTc2MzU0NzMwMzMzNzU2MzM0NjNmNDYzYjQzMzQ2ODNiNjMzZDQ1Mzg0MzMzNzUzOTYzMzM2NDM1NDMzMzY4MzgzMzMzNDczMTMzM2Q0MjNhNzMzNDM1MzI2MzMzNDUzNzM2Mzc0NjNiNjMzOTY2MzE0MzNhNzczMjUzM2Q2MTMwNzMzODU1Mzk1MzNhNzEzOTQzM2Q2NzM5MzMzNDY4M2U2MzNlNDUzNjYzMzI0MjMxMzMzMDczMzk3MzM0NjMzZTQzMzY1NDM4NzMzODYzMzM2NjM4NzczOTUzMzY3MzM1MzYzMDU3MzY1MzM1NjEzMzYzMzg0NjNmNDMzNjQ4MzU0MzMzNDUzMzYzMzQ2NjMwNTMzNDc1MzI1MzNmNDMzNTUzM2Q2NTMxNDMzMTcxMzU1MzNhNjMzZTQzM2M2NzM1NzMzMTc3M2Y0MzMzMzYzNTUzMzMzNjM3NjMzZDQyMzM0MzMxMzMzYjYzM2E1MTNhNTYzMTc3Mzg0MzNmNDMzMjU2Mzc2NjMxMzMzNzc0Mzg2MzMzNzYzMTczMzI1MTM3NjYzYzY0MzU1MzM4NDM2MjY3MzU0MzY4NDczMTU1MzU2NTNhNzIzZTY3MzU3ODM5NjMzZjYxNjM2NTNiNjIzZTYzMzk0ODMwNTQzNTYxMzI3NTMyNTM2NzU0MzQ0MjM0MzMzMzc2M2Y0NDM2NTIzMTQ3MzY2MjMzNzMzZTZmMjE2MjMyMzYzOTYzMzAzNzM4NjQ2YTU2M2E3MTM5NjYzYTQ1M2E2NjMxNDIzZTQ3MzY2NDM5NjczZjYzMzgzNzM0NTM2ODM3MzQ2MzY3NDczMzUzNzQ2NTI0NTM2YjQ3Mzg0MzY2NDczNTc0NjIzNDM1NjMzMzU2Mzg1NDNkNjUzZDYyMzI1NjNhNTIzYjY3MzY3MTM3NDQzMTU3MzU0NjMyMzYzNzY1MzU0MTM4NDczNTQwMzM3MzM0NDMzODc2MzQ1MTM0NjczNTRmMjMzODNiNDMzNDY4NzQ1MzdiNjU2ZjQzNjU1Mjc3NTU3YzRmNjg2Mzc5M2YyMjU0N2Y0NTY5M2U2NjRlMjA1MjZmNjM3MDdkNmI2MTY0MzU2NTUyNzg1NDdhNjM3NTVmMjc3ZjI0NWEzNjczNzI0MDdiNDQ3NDU0NzQ1ODY=') % _id
    json_data = httptools.downloadpage(url, headers={'watchsb': 'streamsb'}, alfa_s=True).json

    if isinstance(json_data, dict) and json_data.get('stream_data', {}) and json_data['stream_data'].get('file', ''):
        video_url = json_data['stream_data']['file']
        if video_url:
            video_urls.append(["m3u8 [StreamSB]", video_url])

    return video_urls


def get_data_zw(host, item, **kwargs):

    pagination = False
    result = dict()
    url = eval(unmix("ZDQyMjk1MDcyNzg2MTUwNzc0ZTIyNDI3YzQ1NjUzNjc1NzI3NjQ1NjQ2Mzc2N2YyYTYzMzU2ZjZjNDY3NDU5NjUzNDc0NDE2NDRlNjU3MjcwNTU2YTc0Nzk0YzY4NjE2YTcyMjU0MDI2N2IyNzMwMmM0NDc0NzM3YTdmNjQ1ODY="))
    post = eval(unmix("MzRkN2Q0MDMxMzIzNDYwMjg3YTM1NzIyYjQ4NjY2NDczNDc2MzNlNjc1NTYxNGM2MDMyMjc0MDJhNGMyMDM0NzA3Mjc4NzE2NTM0Nzk0MzczNGUyYjRkNjAzNTZmNjQ3NjY5NjY2MDIxM2EzZDYyMjM3NDc0MzI3NjMxNjYzNDdmNDM3MzQyMjMzMDJmNGMyMTQyMmI2YzY0MzE2YzY0NzE1ZjZiNjQ1NzcxNjk1NDc4NTM3MjY5NjA1YzQ1NDI3YTY1NjkzZTYxNDU2MDM0N2I2MjYwNWY0NTYyMmY0MDI5N2EzNzQyMjI2ZjY2NzQ2NzdmNmE3NDc0NTU2MjZkNmE2MjIyNGI3"))

    if not kwargs.get("section", False):
        post.update(eval(unmix("MjVkNzc1OTcxNTI3NjQ0N2E3ZTZiNDU3MDdmNmQ2MzY5M2UyODNkNjM1NTYzNDQ3MDU5Njc3MDI1NmEzMzUyMjk1ZDUyNzAzMDdiNTczZDUwMzYzMDUxNmU2YjU5NzM3NDQ1NjAzZTZiNjE2ZTYwNTkzODYxNjM2MTcyNzUzMTYyNzU2YTUzNzI1MjI1NzAyNzVjMjQ2Mjc5NTE2MzU1NjA1OTc5M2UyNzNkNjk1NTYyNDQ3ZDY5Njg3MDI1N2EzYjYyMjU1ZDVhNzAzMDViNTM3ZDUzNzQzNTUxNjc3YjVmNjM3NjU1NjQ2ZTY4MzE2OTYwNTI0ODZhNTM2ZDQyNzM2MTY3NzU2NDMzNzU0MjI0NDAyOTVjMmI2NTY4NjI3MTNlNmE0NTYyNTc2MTNlMjk1ZDY1NDU2NDQ0NzU3OTY1NzAyYjRhMzQ0MjJmNmQ1MTUwMzQ2YjUxN2Q1MTc1MzM0MTY0NWI1ZTYzNzQ1NTY3N2U2NTYxNjk3MDUyMzg2NDczNmE3Mjc3NDE2MjY1NjU0MzczNDIyMzUwMjc3YzI4Nzg2MjczNjg3MjdhNjE2MzY1NjI1Mzc2M2UyNzZkNjczNTYyNjQ3NTM5NjQ0MDI2NGEzYTQyMjE0ZDViNjU2NTU1NzY0YzYzNzE2ODc2NzE2YjU1NDg2NDczNjczMjc2MzE2MDc1NjQ1MzcyNTIyNTViNw==")))

    headers = eval(unmix("ZDZkNzk3NDcyNzM3ZjZmNjQzODY5NjAyNDc1MmQ0MDI3NzIyZTYwNzk3ODYyNTA3ODNlMmM2MjdkNmY2NTM0NmM2MTZmNDM2NjUzNzk0NTdlNDI2MDVmMjc0NTY1N2Q2YTVmNmE1ODZlNmYyNTUzNzgzNTJjNDIyZDQwMjQ3YTM4NzIyNDUyNzQ1NTZmNDI3OTM1NjI0NjYxNzU2YTQyNzg1MjJmNGI3"))

    data = httptools.downloadpage(url=url, post=post, headers=headers, alfa_s=True).json

    if kwargs.get("section", False):
        result["genres"] = eval(unmix("ODdkNTQzMjJlNDUzZjQxNjg1MjI5M2I1ZTRkNTkzMjI4NTM3MDdlNjI1ZjZjNDk2Nzc0NzM3MDc2M2Y2NzMyMjU0YjU3NmQ1NzMyMjM2MzdhNTU2NTdlNjk2MTY3NjA1MTc4NmE2MzY4NTI3NTQxNjkzNTYxNDM3YzQyMjY3YjVlNDE2YjY0NzA1MTY2NzQ2"))
        result["years"] = eval(unmix("NzRkNWY0MjJlNDQzZTYxNjc0MjI4NGI1YTRkNTgzMjIyNTM3ZTRlNjMzZjZiNjk2Mzc0NzY1MDc2NmY2NjQyMjUzYjVlNmQ1MTQyMjAzMzcwNTU2ZTZlNjAzMTYxNTA1YTc4NjY3MzY0NzI3OTMxNmI0NTZkNjM3MDMyMjk0YjVhNjE2YzQ0Nzg1MTY5NDQ2"))
        result["countries"] = eval(unmix("MzNkNTI3MjI5NTYzNDQxNjY0MjI4NGI1NTdkNTA1MjI5NjM3ODdlNjQ3ZjYzNzk2NDQ0NzQ0MDdkNmY2OTQyMjI0YjVlNGQ1MTMyMjU0Mzc1MzU2NTNlNjEzMTY0NDA1ODU4NjM2MzYwMzI3NDUxNjc3NTYzNTM3NDYyMjk3YjUyMzE2YzQ0N2I0MTYzNTQ2"))

    if data["recordsFiltered"] > 20:
        pagination = True

    data = data.get("data", {})

    result["matches"] = data
    result["pagination"] = pagination

    return result
    
    
def find_alternative_link(item, torrent_params={}, finder_com=False, timeout=-2, 
                          debug=False, cache=False, mute=False, alfa_s=True):
    import time
    from collections import OrderedDict
    from lib.cloudscraper import cf_assistant

    try:
        ssl_status = False
        import ssl
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.poolmanager import PoolManager
        
        class TLSHttpAdapter(HTTPAdapter):
            def init_poolmanager(self, connections, maxsize, block=False):
                self.poolmanager = PoolManager(num_pools=connections,
                                               maxsize=maxsize,
                                               block=block,
                                               assert_hostname=False,
                                               ssl_version=ssl.PROTOCOL_TLSv1_1)
        
        ssl_status = True
    except:
        logger.error(traceback.format_exc())

    quality_alt = torrent_params.get('quality_alt', '')
    domain_alt = torrent_params.get('domain_alt', '')
    language_alt = torrent_params.get('language_alt', [])[:] or item.language[:]
    if language_alt and not 'DUAL' in language_alt: language_alt += ['DUAL']
    retries = torrent_params.get('retries', 2)
    next_page = torrent_params.get('find_alt_link_next', 0)
    torrent_params['find_alt_link_next'] = 0
    season = torrent_params.get('find_alt_link_season', 0)
    season_low = season
    if season and not isinstance(season, int):
        season = str(season).split('-')
        if len(season) > 1:
            season_low = int(season[0])
            season = int(season[1])
    headers = torrent_params.get('headers', OrderedDict())
    torrent_params['find_alt_link_result'] = []
    torrent_params['find_alt_link_language'] = []
    
    if httptools.TEST_ON_AIR:
        return torrent_params

    patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?([\w|\-]+\.\w+)(?:\/|\?|$)'
    patron_host = '((?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+)(?:\/|\?|$)'
    matches = []
    matches_raw = []
    url_find = ''
    quality = []
    extraPostDelay = timeout if timeout >= 0 else 0
    assistant = ssl_status \
                or filetools.exists(filetools.join(config.get_data_path(), 'alfa-mobile-assistant.version')) \
                or filetools.exists(filetools.join(config.get_data_path(), 'alfa-desktop-assistant.version'))

    btdigg_status = config.get_setting('btdigg_status', server='torrent', default=False)
    success = False
    code = 429
    data = ''
    elapsed = 0

    finder_dw = unmix("YzZkMzYzMDc5MzYyNzYwMzY3ZDM2NDI3MDM1NjQ3NDYzNzI3NzVmNjAzZjM5Mzg2MTQzNmQ2MjdlNDE2ODY1NjY2MzczM2YyNjRlNGY0ZjQyNDk0MzZlNDc0ZjQ0M2UyMzU0NjMzOTczNzM3MTQ2NjM0YTdlNmQ2MTY1NzI0YTY1NDYzNjc1Mzg0YTc3NzY2NzNhNjg2NDZjNjM2MjVjNjk0OTZmNmE2ZTQ1NzU3NDc0NDQ3ODNmNmQ2ODc2Njc3OTdhNzYzMDc3MzQ3NDVlNjQ2MjY5NjM3NjRkNjUzNTYyMzE3ZTRkNjU1YzY0NDI2MTYzM2M0YjYzMzk2NTMyN2Q2MTdhNmE3NjMxN2U0NDY4NTA3NTYyMzg2YjY1N2U2OTU5Njc1NzYyMzc2NjM3NjY1OTZkNDQ2Nzc0Nzk2MjYxNGYyYTVmMjI1YTNjNDM3YzQwNzUzNDdjNjQ3YzY4Ng==") + str(next_page)
    finder_cw = unmix("NDZkMzg2MDcyNDYyZDQwMzk1ZDM2MzI3OTc1NjY2NDZhNzI3YzZmNjM1ZjMzNTg2NDQzNmQ2MjczNjE2Njc1NjU2Mzc5NmYyMzRkNmE2ZjYyMzM2MzVlMjg2NzYxNzk2MDc0NjIzNDc2NDI2ZDZmMjE2ZjI2N2EzNjczNzk0MDc1NzQ3YzQ0N2M0ODY=") + str(next_page)
    if finder_com or assistant:
        finder = finder_cw
    else:
        finder = finder_dw
    finder_alt = unmix("NTRmMjg0ZDY4NmY2MzMzNmE0ZTI4Nzc2NTU5NmE1NDY5NjQ3MzQyNjc0ZjJkNmYyNjRhMzczMzcxNzA3MTQ0NzczNDdlNDg2")
    gateways = eval(unmix("NjVkNTI1NzI4NWY2ZTQ0N2E1ZTJiNjI2MDU1NjE1Nzc1NDIzODcyNzQ1ZjY0NTQ3NDc3MmQ2MDIxM2MyODM3MmY0NDc0NjU2NzcwN2Y0ZTJhNmU2MjdmNjM0OTYyNWU2NjNmNjgzNzIwMzAyNDVjMmE1NzIyNjM3MjQ3Nzg1ZTI5N2U2NDNmNjM1OTZhNGU2OTVmNjgzNzJkNGI1"))
    sufix = unmix("NDRlNDk3ZjQ3NDk0NTVlNDk1ZjQ=")
    error = unmix("MDMyNTU1ZjRmNjI1MTQyNWM2NTQ=")
    domain = scrapertools.find_single_match(item.url, patron_domain)
    domain_cw = scrapertools.find_single_match(finder_cw, patron_domain)
    dot = '.com'
    ua = headers.pop('User-Agent', '') or unmix("MTcxMzE0MzMzNWUyYzQ2M2Q0MTMwMzMzMTY0Mzk2ZTI4NDAzNDNlMjMzNDMzMzgzMzZmMjE0MjVhNTA1ZjRmNGE0MDI1NjYzYTUzMzU1ZTJhNjczMTYzMzQ0NTMyNGYyMjM5NjQ2Mjc0MzE2Mzc2NmE3MTYzMzM1MzMwMmI2OTMyNzAzNzcxM2E1ZTJlNDgzNDQ1MzgzNzM5NzQzNjRlMjU2MDM1NWUyNTU4MzM2OTNkNGYyNjY1NmU2ZDYzNmY2MzcyN2E0ODY4NzM0MjcwMjM2OTI4N2Y2OTZiNjQ1MzZhNjU2NjU3NDU0MDI0NTU2NjViNjc2OTY5NGM2MDUwMjUzYzJhNmM0MzVkNDQzNDU2NDg0NjNiNDMzODJhNTAyYTY2MzM0MzM4NGUyYzQ3MzkzMzM3NTUzNjNmMmQ0NDczNDk2ZDZiNGE1MjY5NDU2YzY3NTU1NTY5NWM2YzYwNzU0MDcwNzE0NTcwMjgzOTJkNDQzYzY2MzY3NzVjNmY0MjU3NTk1MDJhNWIzYTUwM2I2ZTI2NTAzOTUxMzA1MDI0NTQ1MTZlNDc3MDI5NTM3MDM3N2E1ZjY3NzQ2MjdlNjY2OTYxNTc1ZTQ4MjEzMDI4NjAzNDVlMmE0NTMxN2YyMjQxNjQ1YzY0M2M2OTQ5Njc3YTcxNGY2NzZkNA==")
    cn = unmix("OTQ1NjE2MzY0NmU2MTMxNjYzMjc4NjE2ZTY1NmQ2YzY1NDM2NDRmNTU2NjY2NTM2")
    domain_base = unmix("NDMxN2M0ODY4Njg3YTY5NjAzZDY0NGY2NTU0NzI0MTY=")
    domain_repl = ''
    if domain_base and domain_repl and domain_base in domain_alt: domain_alt = domain_alt.replace(domain_base, domain_repl)

    if item.btdigg:
        url_find = item.btdigg
    if not url_find:
        if item.contentType == 'movie':
            contentTitle = scrapertools.slugify(item.contentTitle.lower(), strict=False).strip()
            contentTitle = contentTitle.replace('(v)-', '').replace(' -varios-', '').replace(' -serie-', '')\
                                       .replace(' -[v. extendida]-', '').replace(' [TERM]', '')
            url_find = contentTitle
            if ' ' in contentTitle: contentTitle = contentTitle.split(' ')[-1]
        else:
            contentTitle = scrapertools.slugify(item.contentSerieName.lower(), strict=False).strip()
            contentTitle = contentTitle.replace('(v)-', '').replace(' -varios-', '').replace(' -serie-', '')\
                                       .replace(' -[v. extendida]-', '').replace(' [TERM]', '')
            url_find = contentTitle
            if ' ' in contentTitle: contentTitle = contentTitle.split(' ')[-1]
            if season and season == season_low:
                url_find += ' Temporada %s' % str(season)
            elif not season:
                url_find += unmix("NDYzNzE3NTI1NDM3ODc1Mjc1ZTIyNDA3YjYxNjg2MzQ5NjAy") % (item.contentSeason, str(item.contentEpisodeNumber).zfill(2))
        patron = unmix("YTU5Mjg1MDdhNjk2NzcyNzM1MjY4NzU2NDY3NTY0YjQ4NzQ2MzVjNWE3YzdkNjQyNTQ2NTI3NDUzNTQ0YTU4NDQzYzc4MzA3NzdkNzk2NDMzNmMyNzMwMzAzYjc4NjQ2MTVjNTk0YTM1NmYzMzU4MjAzOTI4NDk2MDdmMzEzODI=")
        if quality_alt:
            quality = quality_alt.strip().split(' ')
            #url_find += ' %s' % quality_alt
        else:
            quality = [scrapertools.find_single_match(item.quality, patron).lower()]
            #url_find += ' %s' % quality[0]
        if domain_alt: domain = domain_alt
        url_find += ' %s' % domain.split('.')[0]
        url_find = url_find.replace(' ', '+')
    
    post = post_save = unmix("MzZkMzM1MTc4NjYyMjMxMzg1ZDMxNzQ1NzY1NDg3NzRhNjQ3ODYyNzM0NTY1NTY3MTRlNjc0ZjYyNDM2") + url_find.replace(' ', '%2B')
    if domain_base and domain_repl: post_save = post_save.replace(domain_repl, domain_base)
    inicio = time.time()
    session = requests.session()
    session.verify = False
    try:
        session.mount(finder_cw.rstrip('/'), TLSHttpAdapter())
    except:
        ssl_status = False
        assistant = ssl_status \
                    or filetools.exists(filetools.join(config.get_data_path(), 'alfa-mobile-assistant.version')) \
                    or filetools.exists(filetools.join(config.get_data_path(), 'alfa-desktop-assistant.version'))
        if finder_com or assistant:
            finder = finder_cw
        else:
            finder = finder_dw

    for x in range(retries):
        finder += unmix("MzUzNzI1NTIyM2QzNDUxNzQ0NjI=") % url_find
        sufix_out = random.choice(gateways)
        gateways.remove(sufix_out)
        finder_out = finder.replace(sufix, sufix_out)
        referer = scrapertools.find_single_match(finder_out, patron_host)
        referer += '/' if not referer.endswith('/') else ''
        success = False
        suf = '' if x == 0 else '-R'
        code = 429
        response = {}
        headers_out = headers or OrderedDict()
        headers_out["Referer"] = referer
        if ua: headers_out["User-Agent"] = ua
        try:
            if sufix_out not in finder_out:
                sufix_out = dot
                if not btdigg_status or (isinstance(btdigg_status, int) and btdigg_status != code):
                    headers_com = headers_out.copy()
                    response = session.get(finder_out, timeout=5, headers=headers_com, allow_redirects=False)
                    success = response.ok
                    code = response.status_code
                    data = response.text
                    elapsed = response.elapsed
                    if not debug and (code != 200 or not btdigg_status): config.set_setting('btdigg_status', code, server='torrent')
                if isinstance(code, int) and code in [429, 503]:
                    data, response = cf_assistant.get_source(finder_out, response, timeout=timeout, debug=debug, 
                                                             extraPostDelay=extraPostDelay, retry=False, blacklist=True, 
                                                             retryIfTimeout=True, headers=headers_out, 
                                                             cache=cache, mute=mute, alfa_s=alfa_s)
                    code = response.status_code
                    if code == 201:
                        config.set_setting('btdigg_status', code, server='torrent')
                        code = 200
                    success = True if code == 200 else False
                    elapsed = time.time() - inicio
                elif isinstance(code, int) and code in [200]:
                    cf_assistant.freequency([domain_cw, 'Cha,0.0.0,0,%s0,OK_Cok%s' % (config.get_system_platform()[:1], suf)])
                else:
                    cf_assistant.freequency([domain_cw, 'Cha,0.0.0,0,%s0,KO_Web%s' % (config.get_system_platform()[:1], suf)])
                if not success:
                    finder = finder_dw
                    continue
        except Exception as e:
            logger.debug('Error TRY: %s -%s' % (sufix_out, str(e).split(':')[-1]))
            logger.debug(post_save)
            #logger.error(traceback.format_exc())
            cf_assistant.freequency([domain_cw, 'Cha,0.0.0,0,%s0,KO_WebE%s' % (config.get_system_platform()[:1], suf)])
            config.set_setting('btdigg_status', False, server='torrent')
            finder = finder_dw
            continue
        
        try:
            if not success:
                response = session.get(finder_out, timeout=5, headers=headers_out)
                success = response.ok
                code = response.status_code
                data = response.text
                elapsed = response.elapsed
                if success:
                    cf_assistant.freequency([domain_cw, 'Cha,0.0.0,0,%s0,OK_Tor%s' % (config.get_system_platform()[:1], suf)])
                else:
                    cf_assistant.freequency([domain_cw, 'Cha,0.0.0,0,%s0,KO_Tor%s' % (config.get_system_platform()[:1], suf)])
        except Exception as e:
            logger.debug('Error TRY: %s -%s' % (sufix_out, str(e).split(':')[-1]))
            logger.debug(post_save)
            #logger.error(traceback.format_exc())
            cf_assistant.freequency([domain_cw, 'Cha,0.0.0,0,%s0,KO_TorE%s' % (config.get_system_platform()[:1], suf)])
            if 'timed out' in str(e).lower(): break
            continue

        if not success:
            logger.debug('Error NOK: %s - %s: -%s' % (sufix_out, time.time()-inicio, str(code).split(':')[-1]))
            logger.debug(post_save)
            if 'Cloudflare version 2' in str(code): break
            if '429' in str(code):
                if dot in finder_out:
                    finder = finder_dw
                    continue
                break
            if 'timed out' in str(code).lower(): break
            continue
        else:
            elapsed = time.time() - inicio
            data = re.sub(r"\n|\r|\t|\s{2,}|(<!--.*?-->)", "", data).replace("'", '"')     # Reemplaza caracteres innecesarios
            patron = '<div\s*class="torrent_name"[^>]*>\s*<a\s*style="color[^>]*href="([^"]+)">'
            patron += '(.*?)<\/a>\s*<\/div>.*?<span\s*class="torrent_size"[^>]*>([^<]*)<\/span>'
            patron += '(.*?)<a\s*href="(magnet[^"]+)"'
            matches_raw = re.compile(patron, re.DOTALL).findall(data)
            if not matches_raw:
                logger.debug('Error PATRON: %s' % post_save)
                logger.debug(data)
                continue
            patron_found = '>(\d+)\s*results\s*found\s*<'
            try:
                torrent_params['find_alt_link_found'] = int(scrapertools.find_single_match(data, patron_found))
            except:
                torrent_params['find_alt_link_found'] = 0
            patron_found = '<a\s*href="[^"]+p=(\d+)[^>]+>\s*Next'
            try:
                torrent_params['find_alt_link_next'] = int(scrapertools.find_single_match(data, patron_found))
            except:
                torrent_params['find_alt_link_next'] = 0
            logger.info('%s: %s; %s; %s' % (sufix_out, elapsed, torrent_params['find_alt_link_next'], 
                                            torrent_params['find_alt_link_found']))
            break
    if not success:
        if item.btdigg: 
            matches.append([error, error, error, error, error])
        torrent_params['find_alt_link_result'] = matches
        torrent_params['find_alt_link_next'] = 0
        return torrent_params
    
    if success:
        for scrapedurl, scrapedtitle, scrapedsize, scrapedfiles, scrapedmagnet in matches_raw:
            q_ = ''
            title = scrapertools.remove_htmltags(scrapertools.unescape(scrapedtitle))
            try:
                q_ = scrapertools.find_single_match(title, '[\s|\)]\[([^\]]*)\]')
            except:
                q_ = ''
            if not item.btdigg:
                
                if not contentTitle in title.lower():
                    continue
                if item.contentType != 'movie' and not season \
                                               and not 'Cap.%s%s' % (item.contentSeason, str(item.contentEpisodeNumber).zfill(2)) in title:
                    continue
                if season:
                    try:
                        seacap = int(scrapertools.find_single_match(title, 'Cap.(\d)\d{2}'))
                    except:
                        seacap = 1
                    if seacap < season_low or seacap > season:
                        continue
                if quality and not q_:
                    continue
                for q in quality:
                    if q.lower().replace('webrip', '') in q_.lower() or q.lower().replace('webrip', '') in title.lower():
                        break
                else:
                    if quality: continue

            url = scrapedurl
            if not url.startswith('http'): url = 'https:%s' % url
            url = url.replace(referer, finder_alt)
            size = unmix("NjMwMjQ3ZDU3NDI0OTVmMmE1YjViNmQ1YzQyNTc1ZjQyNWM0MjdmNDEzMzQ2M2YyYjZiNTU2NzZhNjc2NTQ5Njc0NDQ4NWQ1NzY0NmE0NTYzNzI3MTYwMmU0MjU5NGY0ODVjNDU3ZjQ2MzM0NjdiNTgzZDViNDI1NjRmNDg2YzQ2NWY0MjYzNGE0ZjJlNGI1MjM0NTM1MjQ4NmQ1NDRlNjIzNTY2NzU2YTYyNzMzNzZkNjU2OTRkNmY2OTY4NWM2OTYwMjA1MjU3N2Y0MjZjNDQzZjQ5NjM0ODNiNTU1ZDU1NTI0OTRiNQ==")
            if '.rar' in scrapedfiles:
                size += unmix("MDdkNTI1MjUzM2Y0ZDZjNGU0ZjRlNDM0NjVmMjE3YjU0NGQ1ZTQyNDYzZjIyNWI1OTZkMjk0MjU4NzE0MTcyNTU1ZDUyNzI0ZDRiNTM1ZDU4NTE2YjY0NzY2ZTYzNDU2ZTQ3NjU1MTY5M2Q2NzUwMjY2MjU3N2Y0NjZjNDI3ZjRhNTM0NDRiNQ==") + scrapertools.unescape(scrapedsize)
            else:
                size += scrapertools.unescape(scrapedsize)
            title = unmix("MzUwMjg3ZDU5NjI0MjVmMjgzYjU1NWQ1NzMyNWE2ZjQwNWM0NDdmNDI1MzQzN2YyOTViNTkzNzYxNzc2YTU5NjU3NDRhNmQ1NzU0Njg3NTYzNTI3MTUwMjg2MjU4N2Y0MzVjNGY0ZjRkNjM0NzViNTk3ZDU5MzI1ODVmNDM1YzQxNGY0OTUzNDk2ZjI1NmI1MjU0NWI2MjQzN2Q1NzdlNjM0NTYxNzU2NDMyN2M2NzY1NDU2NDZkNmQ2OTY5N2M2YTUwMjUzMjU4NWY0NjVjNDczZjQzMzM0NTRiNTc1ZDVhNzI0NjNiNQ==") + title
            
            torrent_params['find_alt_link_language'] = []
            if 'dual' in title.lower() or (('cast' in title.lower() or 'spanish' in title.lower())\
                      and ('eng' in title.lower() or 'ing' in title.lower())):
                torrent_params['find_alt_link_language'] += ['DUAL']            # añadimos DUAL
            elif 'cast' in title.lower() or 'spanish' in title.lower():
                torrent_params['find_alt_link_language'] += ['CAST']            # añadimos CAST
            if 'engl' in title.lower() or 'ingl' in title.lower():
                torrent_params['find_alt_link_language'] += ['VOS']             # añadimos VOS
            if 'lat' in title.lower():
                torrent_params['find_alt_link_language'] += ['LAT']             # añadimos LAT

            if not item.btdigg:
                for lang in language_alt:
                    if 'OTHER' in lang: break
                    if lang in torrent_params['find_alt_link_language']: break
                    if lang.lower() in title.lower(): break
                else:
                    if language_alt: continue
            
            matches.append([url, title, size, q_, scrapedmagnet])

    if not matches and matches_raw and next_page == 0:
        logger.debug('No MATCHES: %s' % post_save)
        logger.debug(matches_raw)
    torrent_params['find_alt_link_result'] = matches
    return torrent_params