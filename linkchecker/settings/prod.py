from base import *

PROCESS_URLS = -1

APP_PATH = '/home/ubuntu/apps/linkchecker'

WEB_APP_ENDPOINT = 'http://52.26.247.39'

RESULTS_UPLOAD_URL = 'script/upload'
PROGRESS_STATS_URL = 'script/progress'
INITIAL_DATA_URL = 'data/projects'

# locally save data in this folder
BASE_DATA_PATH = path.join(APP_PATH, 'data/projects')

PROXY_LIST = path.join(APP_PATH, 'proxies.txt')

CONCURRENT_REQUESTS = 200

CONCURRENT_REQUESTS_PER_DOMAIN = 50

REACTOR_THREADPOOL_MAXSIZE = 50

ENABLE_PROXIES = True

JOBDIR = './crawls'