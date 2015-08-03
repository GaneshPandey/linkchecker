from scrapy.extensions import logstats


class LogStats(logstats.LogStats):
    def log(self, spider):
        super(LogStats, self).log(spider)

        # at 1 min interval set progress request
        spider.make_progress_stats_request()
