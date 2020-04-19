from enum import Enum

from argparse import Namespace, ArgumentParser

from .spiders import DaftSaleUsedSpider
from scrapy.crawler import CrawlerProcess

USER_AGENT_SETTING = 'USER_AGENT'


class WebSources(Enum):
    __order__ = 'HOUSES_FOR_SALE HOUSES_FOR_RENT'
    HOUSES_FOR_SALE = 'houses_for_sale'
    HOUSES_FOR_RENT = 'houses_for_rent'

    def __str__(self) -> str:
        return str(self.value)


class Runner:
    def __init__(self) -> None:
        parser = ArgumentParser(description='Extract data from some websites.',
                                prog='web-acraper',
                                usage='web-scraper houses-for-sale --areas-string "dublin-4,dublin-6"')
        sub_parsers = parser.add_subparsers(title='Avalilable crawlers', required=True)
        parser_houses_for_sale = sub_parsers.add_parser('houses-for-sale',
                                                        help='scrape for used houses for sale data')
        parser_houses_for_sale.set_defaults(source=WebSources.HOUSES_FOR_SALE, type=WebSources)
        parser_houses_for_sale.add_argument('--areas-string', type=str,
                                            help='Areas that you are looking for, this is contained'
                                                 ' on the url of the Daft.ie after an advanced'
                                                 ' search selecting the areas of interest.'
                                                 'i.e: "dublin-1,dublin-2"')
        parser_houses_for_sale.add_argument('--min-price', type=int,
                                            help='Minimum price to be searched for.')
        parser_houses_for_sale.add_argument('--max-price', type=int,
                                            help='Maximum price to be searched for.')
        parser_houses_for_sale.add_argument('--min-beds', type=int,
                                            help='Minimum beds to be searched for.')
        parser_houses_for_sale.add_argument('--max-beds', type=int,
                                            help='Maximum beds to be searched for.')

        parser_houses_for_rent = sub_parsers.add_parser('houses-for-rent',
                                                        help='scrape for houses for rent data')
        parser_houses_for_rent.set_defaults(source=WebSources.HOUSES_FOR_RENT, type=WebSources)

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
            self._process.crawl(DaftSaleUsedSpider,
                                areas_string=args.areas_string,
                                min_price=args.min_price,
                                max_price=args.max_price,
                                min_beds=args.min_beds,
                                max_beds=args.max_beds)
        else:
            print("Parse not implemented yet!!")
            exit(1)
        self._process.start()

    def get_arg_parser(self) -> ArgumentParser:
        return self._parser
