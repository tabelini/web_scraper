from enum import Enum

from argparse import Namespace, ArgumentParser

from .spiders import DaftSaleUsedSpider
from scrapy.crawler import CrawlerProcess

DEFAULT_AREAS = 'dublin-1,dublin-2'

USER_AGENT_SETTING = 'USER_AGENT'


class WebSources(Enum):
    __order__ = 'HOUSES_FOR_SALE HOUSES_FOR_RENT'
    HOUSES_FOR_SALE = 'houses_for_sale'
    HOUSES_FOR_RENT = 'houses_for_rent'

    def __str__(self) -> str:
        return str(self.value)


class Runner:
    def __init__(self) -> None:
        parser = ArgumentParser(description='Extract data from some websites for testing.')
        parser.add_argument('source', type=WebSources, choices=WebSources,
                            help='Source from where to extract the data.')
        parser.add_argument('--areas-string', type=str, default=DEFAULT_AREAS,
                            help='Areas that you are looking for link it appears on Daft.ie.'
                                 'i.e: "dublin-1,dublin-2"')

        self._parser = parser

        self.crawler_settings = {
            USER_AGENT_SETTING: 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible;'
                                ' Googlebot/2.1; +http://www.google.com/bot.html)'
                                ' Chrome/80.1.2.4‡ Safari/537.36',
            'ITEM_PIPELINES': {'web_scraper.spiders.JsonWriterPipeline': 250}
        }

        self._process = CrawlerProcess(settings=self.crawler_settings)

    def run(self, args: Namespace) -> None:
        if args.source == WebSources.HOUSES_FOR_SALE:
            self._process.crawl(DaftSaleUsedSpider, areas_string=args.areas_string)
        self._process.start()

    def get_arg_parser(self) -> ArgumentParser:
        return self._parser
