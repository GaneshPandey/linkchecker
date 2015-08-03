# -*- coding: utf-8 -*-

# Scrapy settings for linkchecker project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
from scrapy.settings import default_settings

from os import path

BOT_NAME = 'linkchecker'

INPUT_URLS_FILE_NAME = 'google_scraper.out'
OUTPUT_URLS_FILE_NAME = 'broken_links.out'

# set this in prod env
WEB_APP_ENDPOINT = None

# number of urls to process, set -1 to process all
PROCESS_URLS = -1

ENABLE_PROXIES = False

# Depth settings
DEPTH_LIMIT = 2
DEPTH_STATS_VERBOSE = False

REACTOR_THREADPOOL_MAXSIZE = 20

LOG_ENABLED = True
LOG_LEVEL = 'DEBUG'
LOG_FORMATTER = 'linkchecker.logformatter.LogFormatter'

DOWNLOADER_STATS = True

MEMUSAGE_ENABLED = True
MEMDEBUG_ENABLED = True

DOWNLOAD_TIMEOUT_WEB_APP = 120
DOWNLOAD_TIMEOUT = 30
DNS_TIMEOUT = 30

# handle all status codes
HTTPERROR_ALLOW_ALL = True

RETRY_ENABLED = True
RETRY_TIMES = 2  # initial response + 2 retries = 3 requests
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 408, 403]
RETRY_PRIORITY_ADJUST = 0

# max time to redirect
REDIRECT_MAX_TIMES = 3

SPIDER_MODULES = ['linkchecker.spiders']
NEWSPIDER_MODULE = 'linkchecker.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'
# USER_AGENT = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 200

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 100

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = True

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
EXTENSIONS = {
    # 'scrapy.telnet.TelnetConsole': None,
    # 'scrapy.extensions.corestats.CoreStats': None,
    # 'scrapy.extensions.memusage.MemoryUsage': None,
    # 'scrapy.extensions.memdebug.MemoryDebugger': None,
    # 'scrapy.extensions.closespider.CloseSpider': None,
    'scrapy.extensions.feedexport.FeedExporter': None,
    'scrapy.extensions.logstats.LogStats': None,
    'linkchecker.extensions.logstats.LogStats': 0,
    # 'scrapy.extensions.spiderstate.SpiderState': None,
    # 'scrapy.extensions.throttle.AutoThrottle': None,
}

DOWNLOADER_MIDDLEWARES = {
    'linkchecker.downloadermiddleware.randomproxy.RandomProxy': 101,
    'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': None,
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': None,
    'scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware': None,
    # 'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
    'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': None,
}

SPIDER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': None,
    'scrapy.spidermiddlewares.referer.RefererMiddleware': None,
}

DEPTH_PRIORITY = 0
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'

AUTOTHROTTLE_ENABLED = False
AUTOTHROTTLE_START_DELAY = 0.1
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_DEBUG = True


COMMANDS_MODULE = 'linkchecker.commands'