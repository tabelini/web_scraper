from unittest import mock
from unittest.mock import Mock

import pytest
from web_scraper import Runner, WebSources


@mock.patch('scrapy.crawler.CrawlerProcess')
@pytest.fixture()
def runner():
    result = Runner()
    result._process = Mock()
    return result


@pytest.mark.parametrize('name, value', [('DAFT', 'daft'), ('MY_HOME', 'my_home')])
def test_web_sources_should_return_the_value_in_str(name, value):
    assert str(WebSources[name]) == value


def test_runner_should_call_start(runner):
    runner.run([])
    runner._process.start.assert_called_once_with()
