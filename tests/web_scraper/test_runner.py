from unittest import mock
from unittest.mock import Mock

import pytest

from web_scraper.runner import USER_AGENT_SETTING
from web_scraper.spiders import DaftSaleUsedSpider
from web_scraper import Runner, WebSources

AREAS_TO_LOOK = 'areas_to_look'
MIN_PRICE = 1000
MAX_PRICE = 10000
MIN_BEDS = 2
MAX_BEDS = 4


@pytest.fixture()
def runner():
    result = Runner()
    result._process = Mock()
    return result


@pytest.mark.parametrize('name, value', [('HOUSES_FOR_SALE', 'houses_for_sale'),
                                         ('HOUSES_FOR_RENT', 'houses_for_rent')])
def test_web_sources_should_return_the_value_in_str(name, value):
    assert str(WebSources[name]) == value


@mock.patch('web_scraper.runner.CrawlerProcess')
def test_crawler_should_run_with_provided_settings(crawler_process_mock):
    runner = Runner()
    crawler_process_mock.assert_called_once_with(settings=runner.crawler_settings)


def test_runner_should_start_the_crawler_for_implemented_operations(runner):
    runner.run(runner.get_arg_parser().parse_args(args=['houses-for-sale']))
    runner._process.start.assert_called_once_with()


def test_runner_should__not_start_the_crawler_for_unimplemented_operations(runner):
    with pytest.raises(SystemExit) as exp:
        runner.run(runner.get_arg_parser().parse_args(args=['houses-for-rent']))
        pytest.fail("It should have raised an exception")
    assert exp.value.code == 1


def test_runner_should_parse_daft_with_correct_areas(runner):
    args = runner.get_arg_parser().parse_args(args=['houses-for-sale',
                                                    '--areas-string', AREAS_TO_LOOK,
                                                    '--min-price', str(MIN_PRICE),
                                                    '--max-price', str(MAX_PRICE),
                                                    '--min-beds', str(MIN_BEDS),
                                                    '--max-beds', str(MAX_BEDS)])
    runner.run(args)
    runner._process.crawl.assert_called_once_with(DaftSaleUsedSpider,
                                                  areas_string=AREAS_TO_LOOK,
                                                  min_price=MIN_PRICE,
                                                  max_price=MAX_PRICE,
                                                  min_beds=MIN_BEDS,
                                                  max_beds=MAX_BEDS
                                                  )


def test_crawler_identify_it_self_as_google_bot(runner):
    assert 'Googlebot' in runner.crawler_settings[USER_AGENT_SETTING]
