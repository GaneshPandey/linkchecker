from scrapy import logformatter


class LogFormatter(logformatter.LogFormatter):
    def crawled(self, request, response, spider):
        r = super(LogFormatter, self).crawled(request, response, spider)

        r['msg'] = "%%(proxy)s %s" % r['msg']

        proxy = request.meta.get('proxy', '')

        if proxy:
            proxy = proxy.rsplit('/', 1)[-1]

            proxy = "[%s] " % proxy

        r['args']['proxy'] = proxy

        return r
