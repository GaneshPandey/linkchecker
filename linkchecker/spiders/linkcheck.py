# -*- coding: utf-8 -*-
from os import path
import os
import shutil

from scrapy.exceptions import CloseSpider
from scrapy.http.request import Request
from scrapy.http import FormRequest
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.linkextractors import IGNORED_EXTENSIONS
from twisted.internet.error import DNSLookupError
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from linkchecker.http_codes import *
from linkchecker import utils

from urlparse import urljoin


class LinkcheckSpider(CrawlSpider):
    """Base scrapy spider used to crawl all the links"""

    name = "linkcheck"

    IGNORED_EXTENSIONS = IGNORED_EXTENSIONS + ['msi', 'tar', 'bz2', 'gz', 'asc', 'dmg', 'tgz',
                                               'xz', 'pptx']

    NOT_FOLLOW_TAGS = ['script', 'video', 'iframe', 'embed', 'object']
    NOT_FOLLOW_ATTR = ['href', 'data', 'src']

    ALLOW_ALL_EXTENSIONS = [r'.%s$' % e for e in IGNORED_EXTENSIONS]

    rules = (
        Rule(LinkExtractor(allow=('.*',), tags=('a', 'area', 'link'), attrs=('href',),
                           deny_extensions=IGNORED_EXTENSIONS), callback='parse',
             follow=True,
             process_request='process_request_get'),

        Rule(LinkExtractor(allow=('.*',), deny_extensions=(), tags=NOT_FOLLOW_TAGS,
                           attrs=NOT_FOLLOW_ATTR),
             callback='parse', follow=False, process_request='process_request_head'),

        Rule(LinkExtractor(allow=ALLOW_ALL_EXTENSIONS, tags=('a', 'img',), attrs=('href', 'src',),
                           deny_extensions=()),
             callback='parse', follow=False, process_request='process_request_head'),
    )

    def __init__(self, *args, **kwargs):
        super(LinkcheckSpider, self).__init__(*args, **kwargs)

        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

        self.outfile_path = None
        self.outfile = None

        self.result_uploaded = False
        self.finished_progress_sent = False
        self.initial_data_received = False

        self._progress_stats_url = None
        self._results_upload_url = None
        self._initial_data_url = None

    @property
    def progress_stats_url(self):
        if not self._progress_stats_url:
            self._progress_stats_url = urljoin(self.settings['WEB_APP_ENDPOINT'],
                                               self.settings['PROGRESS_STATS_URL'])

        return self._progress_stats_url

    @property
    def results_upload_url(self):
        if not self._results_upload_url:
            self._results_upload_url = urljoin(self.settings['WEB_APP_ENDPOINT'],
                                               self.settings['RESULTS_UPLOAD_URL'])

        return self._results_upload_url

    @property
    def initial_data_url(self):
        if not self._initial_data_url:
            self._initial_data_url = urljoin(self.settings['WEB_APP_ENDPOINT'], "%s/%s/%s" %
                                             (self.settings['INITIAL_DATA_URL'], self.spider_id,
                                              self.settings['INPUT_URLS_FILE_NAME']))

        return self._initial_data_url

    @property
    def max_depth_limit(self):
        return int(self.settings['DEPTH_LIMIT'])

    def process_request_get(self, r):
        """Set the request method to GET. Also set the error handler"""

        meta = r.meta.copy()
        meta['dont_retry'] = True

        r = r.replace(method='GET', errback=self.error_callback, meta=meta)

        return r

    def process_request_head(self, r):
        """Set the request method to HEAD. Also set the error handler"""

        meta = r.meta.copy()
        meta['dont_retry'] = True

        r = r.replace(method='HEAD', errback=self.error_callback, meta=meta)

        return r

    def get_input_file_url(self):
        """Get the url to the web app where we have file with a
        list of all urls we need to process"""

        spider_id = getattr(self, 'spider_id', None)

        if not spider_id:
            raise CloseSpider("Invalid spider id")
        else:
            url = self.initial_data_url

            return url

    def spider_opened(self, spider):
        """Handler for spider open. Here we init the output file."""

        self.logger.info("Spider id: %s" % self.spider_id)
        self.logger.info("Proxies enabled: %s" % self.settings['ENABLE_PROXIES'])
        self.logger.info("Server endpoint: %s" % self.settings['WEB_APP_ENDPOINT'])
        self.logger.info("Initial data url: %s" % self.initial_data_url)

        if self.settings['PROCESS_URLS'] > 0:
            self.logger.info("Parse %s urls " % self.settings['PROCESS_URLS'])

        file_path = path.join(self.settings['BASE_DATA_PATH'], self.spider_id,
                              self.settings['OUTPUT_URLS_FILE_NAME'])

        if not path.exists(file_path):
            os.makedirs(path.dirname(file_path))

        self.outfile = open(file_path, 'w')
        self.outfile_path = file_path

        self.logger.info("Open file for writing: %s" % path.basename(file_path))

    def spider_idle(self, spider):
        """When spider is idle this mean that there are no request in the queue, which mean that
         spider finished all the links and is about to close. Send here the result and make progress
         100%.
        """

        # only update the progress if we received the initial url
        if self.initial_data_received:
            self.make_progress_stats_request(progress=100, mark_as_finished=True)

            if not self.result_uploaded:
                self.upload_results_request()

    def _requests_to_follow(self, response):
        """Depending on the depth level we need to parse all the links from this page. But when we reached the last level,
        no need to parse the links at all, this is the last level, so we stop processing the page
        """

        depth = response.meta.get('depth', 0)

        max_depth_limit = self.max_depth_limit

        # only extract links if we need more
        if depth < max_depth_limit:
            for r in super(LinkcheckSpider, self)._requests_to_follow(response):
                yield r

    def start_requests(self):
        """This handler is initially called when crawler is started.
         Make request to web app and get the urls list
        """

        url = self.get_input_file_url()

        yield Request(url, callback=self.init_start_urls, priority=1, errback=self.error_callback, dont_filter=True,
                      meta={
                          'dont_merge_cookies': True,
                          'download_timeout': self.settings['DOWNLOAD_TIMEOUT_WEB_APP'],
                          'skip_proxy': True,
                      })

    def init_start_urls(self, response):
        """Having a list of urls, we need to follow each of them and set the depth level as 0"""

        if response.status != 200:
            self.logger.error("Invalid initial request: %s" % response)
        else:
            # remove the depth for this url, it's just used to get the initial url
            # and not to be user in depth calculations
            # TODO this may no be the most elegant solution, but we need a way to dec the depth 1 level
            response.meta['depth'] -= 1

            max_process_urls = self.settings['PROCESS_URLS']

            self.initial_data_received = True

            for i, url in enumerate(response.body.split('\n')):
                if 0 < max_process_urls < i:
                    break
                url = url.strip()
                if url and url.startswith('http') and not url.startswith('#'):
                    r = Request(url, callback=self.parse, priority=1)
                    yield self.process_request_get(r)
                else:
                    self.logger.error("Invalid url: %s" % url)

    def parse(self, response):
        """Any request will get to this callback and check the status code"""

        depth = response.meta.get('depth', 0)

        if response.status == 200:
            # only extract links if we need more
            if depth < self.max_depth_limit:
                return super(LinkcheckSpider, self).parse(response)

    def error_callback(self, failure):
        """Handle any error that may occur during download process"""

        exception = failure.value

        self.logger.error("%s, %s" % (exception, failure.request.url))

        # for now we are interested only on 'host not found' links
        if isinstance(exception, DNSLookupError):
            code = DNS_ERROR

            data = {'url': failure.request.url, 'code': code, 'status': get_code(code)}

            self.insert_data(data)

    def insert_data(self, data):
        self.outfile.write(data['url'])
        self.outfile.write('\n')
        self.outfile.flush()

        self.logger.info("Broken link: %s" % data)

        self.crawler.stats.inc_value('broken_links')

    def get_broken_links_data(self):
        self.outfile.close()

        with open(self.outfile_path, 'r') as f:
            return f.read()

    def make_progress_stats_request(self, response=None, progress=0, mark_as_finished=False):
        """Make request to stats endpoint and update the progress of the crawler.
        The progress itself may not be accurate as needed since we don't really know the
        number ot total links(this number is increased all the time).
        """

        if self.finished_progress_sent or not self.initial_data_received:
            return

        if not response:
            r = Request(self.progress_stats_url, dont_filter=True, priority=10,
                        callback=self.make_progress_stats_request,
                        meta={'progress': progress, 'cookiejar': 'progress',
                              'mark_as_finished': mark_as_finished, 'skip_proxy': True,
                              'download_timeout': self.settings['DOWNLOAD_TIMEOUT_WEB_APP']})

            self.crawler.engine.crawl(r, self)
        else:
            if response.status != 200:
                self.logger.error("make_progress_stats_request: Invalid token from api!")
                return

            progress = response.meta['progress']
            mark_as_finished = response.meta['mark_as_finished']

            token = response.body

            if not progress:
                received_pages = self.crawler.stats.get_value('response_received_count', 0)
                enqueued = self.crawler.stats.get_value('scheduler/enqueued', 0)

                if received_pages and enqueued:
                    progress = int((received_pages * 100.0) / enqueued)

            if progress:
                formdata = {'dir': self.spider_id, 'progress': str(progress),
                            'type': 'broken_links_progress'}

                self.logger.info("Progress stats send: %s" % formdata)

                r = FormRequest(url=self.progress_stats_url, formdata=formdata, dont_filter=True,
                                priority=11, headers={'X-CSRF-TOKEN': token},
                                meta={'cookiejar': response.meta['cookiejar'], 'skip_proxy': True,
                                      'download_timeout': self.settings['DOWNLOAD_TIMEOUT_WEB_APP']})

                self.crawler.engine.crawl(r, self)

                if mark_as_finished:
                    self.finished_progress_sent = True

    def upload_results_request(self, response=None):
        """When spider is done we need to upload data to the web app endpoint"""

        if not response:
            r = Request(self.results_upload_url, dont_filter=True, priority=9,
                        callback=self.upload_results_request,
                        meta={
                            'cookiejar': 'upload',
                            'download_timeout': self.settings['DOWNLOAD_TIMEOUT_WEB_APP'],
                            'skip_proxy': True,
                        })

            self.crawler.engine.crawl(r, self)
        else:
            if response.status != 200:
                self.logger.error("upload_results_request: Invalid token from api!")
                return

            token = response.body

            file_content = self.get_broken_links_data()

            formdata = {'dir': self.spider_id, 'type': 'linkchecker_results', 'file': file_content}

            r = FormRequest(url=self.results_upload_url, formdata=formdata,
                            dont_filter=True, priority=8, headers={'X-CSRF-TOKEN': token},
                            meta={'cookiejar': response.meta['cookiejar'], 'skip_proxy': True,
                                  'download_timeout': self.settings['DOWNLOAD_TIMEOUT_WEB_APP']},
                            callback=self.after_upload)

            self.crawler.engine.crawl(r, self)

            self.result_uploaded = True

    def after_upload(self, response):
        if response.status != 200:
            self.logger.error(response.body)

    def verbose_stats(self):
        """Compute more verbose stats"""

        runtime_diff = utils.date_diff(
            self.crawler.stats.get_value('start_time'),
            self.crawler.stats.get_value('finish_time'),
        )

        self.crawler.stats.set_value('runtime', runtime_diff)

        self.crawler.stats.set_value('memusage/max', utils.convert_size(
            self.crawler.stats.get_value('memusage/max')))

    def jobdir_clean(self):
        """Remove all the persistent data used by job queue"""

        # try to remove all the persistent data from disc
        # We use the persistent only to use less memory so, no need to keep the data
        jobdir = self.settings.get('JOBDIR', None)

        if jobdir:
            self.logger.debug("Remove persistent dir: %s" % jobdir)

            shutil.rmtree(jobdir, ignore_errors=True)

    def closed(self, reason):
        """Called when the spider is closed.

        Here we mostly clean after the spider adn close all open file handlers
        """

        if self.outfile:
            self.outfile.close()

        self.verbose_stats()

        self.jobdir_clean()
