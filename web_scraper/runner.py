from enum import Enum

from argparse import Namespace, ArgumentParser

from .spiders import DaftSaleUsedSpider
from scrapy.crawler import CrawlerProcess

USER_AGENT_SETTING = 'USER_AGENT'


class WebSources(Enum):
    __order__ = 'DAFT MY_HOME'
    DAFT = 'daft'
    MY_HOME = 'my_home'

    def __str__(self) -> str:
        return str(self.value)


class Runner:
    def __init__(self) -> None:

        parser = ArgumentParser(description='Extract data from some websites for testing.')
        parser.add_argument('source', type=WebSources, choices=WebSources,
                            help='Source from where to extract the data.')

        self._parser = parser

        self.crawler_settings = {
            USER_AGENT_SETTING: 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible;'
                                ' Googlebot/2.1; +http://www.google.com/bot.html)'
                                ' Chrome/80.1.2.4‡ Safari/537.36'
        }

        self._process = CrawlerProcess(settings=self.crawler_settings)

    def run(self, args: Namespace) -> None:
        if args.source == WebSources.DAFT:
            self._process.crawl(DaftSaleUsedSpider)
        self._process.start()

    def get_arg_parser(self) -> ArgumentParser:
        return self._parser
