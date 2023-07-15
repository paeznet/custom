# -*- coding: utf-8 -*-
from core import httptools
from core import scrapertools
from platformcode import logger

def test_video_exists(page_url):
    logger.info()
    global server, vid
    server = scrapertools.get_domain_from_url(page_url).split(".")[-2]
    # server = scrapertools.find_single_match(page_url, 'www.([A-z0-9-]+).com')
    vid = scrapertools.find_single_match(page_url, '/e/([A-z0-9-]+)')

    data = httptools.downloadpage(page_url).data
    if "File was deleted" in data\
       or "not Found" in data:
       # or "small" in data:
        return False, "[%s] El video ha sido borrado o no existe" % server
    return True, ""

# https://videovard.sx/e/i4joiqy3fh70
# https://videovard.sx/api/file/status/i4joiqy3fh70
# https://videovard.sx/api/make/hash/i4joiqy3fh70
# {"status":"200","hash":"804460-47-61-1634803013-6c2154eaa9fd7d2fe2e09ee50f618945","server_time":"2021-10-21 07:56:53"}
# POST  https://videovard.sx/api/player/setup

# cmd: get_stream
# file_code: i4joiqy3fh70
# hash: 804460-47-61-1634802749-8f3eeedf0292bfbf99592a04bb44db21

 # {"seed":"ypx4xpp1dmd8fz16",
    # "server_time":"2021-10-21 08:12:58",
    # "status":"200",
    # "src":"uYktGlYwxOVihp5jk8nUt3NlGhXN0Evq51z-hedR7HMa6UiLI3hDUWpv3Ft08uYj2f6W0Gq9ih2ZLqvDRIH1URKMrk8f0wbgbIheBxWYG2VINvmXpUb1wfMHjjrFkIoCpBZdX9dpP89uy2Ug4zAAhc-I4iENibCumH0eI8OGV2qBQZAQVHucurfVmA2YXou2",
    # "tracks":[]}

# https://content-videovard-delivery-s29.videovard.to/drm/hls/ivs5x4zgurypab7wfwbyx3zffkxq5y3bfynf73uqzav2wsqyveiquf6jj6ea/index-v1-a1.m3u8
# https://content-videovard-delivery-s29.videovard.to/drm/hls/ivs5x4zgurypab7wfwbyx3zffkxq5y3bfynf73uqzav2wsqyveiquf6jj6ea/seg-7-v1-a1.ts

def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    hash_url = "https://videovard.sx/api/make/hash/%s" %vid
    data = httptools.downloadpage(hash_url).data
    hash = scrapertools.find_single_match(data, '"hash":"([^"]+)"')
    post_url = "https://videovard.sx/api/player/setup"
    post = {"cmd": "get_stream", "file_code": vid, "hash": hash}
    data = httptools.downloadpage(post_url, post=post, referer = post_url).data
    logger.debug(data)

    # data = scrapertools.find_single_match(data, '"files":(.*?)"quality"')
    # patron  = '"([lh])q":"([^"]+)"'
    # matches = scrapertools.find_multiple_matches(data, patron)
    # for quality, scrapedurl in matches:
        # url =  scrapedurl.replace("\/", "/")
        # if "l" in quality: quality = "360p"
        # if "h" in quality: quality = "720p"
        # video_urls.append(["[%s] %s" %(server,quality), url])
    return video_urls

