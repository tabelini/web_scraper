from enum import Enum

from argparse import Namespace, ArgumentParser

from .spiders import DaftSpider
from scrapy.crawler import CrawlerProcess


class WebSources(Enum):
    __order__ = 'DAFT MY_HOME'
    DAFT = 'daft'
    MY_HOME = 'my_home'

    def __str__(self) -> str:
        return str(self.value)


class Runner:
    def __init__(self) -> None:
        self._process = CrawlerProcess()

        parser = ArgumentParser(description='Extract data from some websites for testing.')
        parser.add_argument('source', type=WebSources, choices=WebSources,
                        help='Source from where to extract the data.')

        self._parser = parser

    def run(self, args: Namespace) -> None:
        if args.source == WebSources.DAFT:
            self._process.crawl(DaftSpider)
        self._process.start()

    def get_arg_parser(self) -> ArgumentParser:
        return self._parser
