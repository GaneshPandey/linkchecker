from scrapy.commands import crawl
import os


class Command(crawl.Command):
    def process_options(self, args, opts):
        super(Command, self).process_options(args, opts)

        spider_id = opts.spargs.get('spider_id', None)

        # set the JOBDIR to include the spider id
        jobdir = self.settings.get('JOBDIR', None)

        if spider_id and jobdir:
            jobdir = os.path.join(jobdir, spider_id)

            self.settings.set('JOBDIR', jobdir, priority='cmdline')
