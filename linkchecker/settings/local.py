from base import *
from urlparse import urljoin

# LOG_LEVEL = 'INFO'

PROCESS_URLS = -1

APP_PATH = '/Users/geo/PycharmProjects/linkchecker'

WEB_APP_ENDPOINT = 'http://52.26.247.39'

PROGRESS_STATS_URL = 'script/progress'
RESULTS_UPLOAD_URL = 'script/upload'
INITIAL_DATA_URL = 'data/projects'


BASE_DATA_PATH = path.join(APP_PATH, 'data/projects')
PROXY_LIST = path.join(APP_PATH, 'proxies.txt')

ENABLE_PROXIES = True

DOWNLOADER_MIDDLEWARES = {
    'linkchecker.downloadermiddleware.randomproxy.RandomProxy': 101,
    'scrapy_crawlera.CrawleraMiddleware': 600,
    'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': None,
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': None,
    'scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware': None,
    # 'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
    'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': None,
}

JOBDIR = './crawls'

CONCURRENT_REQUESTS = 16

CONCURRENT_REQUESTS_PER_DOMAIN = 10

REACTOR_THREADPOOL_MAXSIZE = 8
