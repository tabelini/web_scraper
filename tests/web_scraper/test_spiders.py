from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest
from scrapy.http import Response

from web_scraper.spiders import DaftSaleUsedSpider, DAFT_ADDRESS, DUBLIN_CITY, PROPERTIES_FOR_SALE, \
    PROPERTY_CARD_SELECTOR, LINK_SELECTOR, DaftExtractor, PROPERTY_TYPE_SELECTOR, \
    BER_RATING_IMAGE_SELECTOR, PRICE_SELECTOR, ExtractorException, QUICK_DETAILS_SELECTOR, \
    FLOOR_AREA_SELECTOR, MAIN_ADDRESS_SELECTOR, EIR_CODE_SELECTOR, STREET_VIEW_SELECTOR, \
    DESCRIPTION_SELECTOR, STATISTICS_SELECTOR

PROPERTY_TYPE = 'Property type'
PROPERTY_TYPE_RAW = '\n            Property type\n    '

BER_RATING_RAW = 'https://c1.dmstatic.com/944/i/ber/ber_A1.svg'
BER_RATING = 'A1'
BER_RATING_RAW_SINGLE_CHAR = 'https://c1.dmstatic.com/944/i/ber/ber_G.svg'
BER_RATING_SINGLE_CHAR = 'G'
BER_RATING_RAW_EXEMPT = 'https://c1.dmstatic.com/944/i/ber/ber_SINo666of2006exempt.svg'
BER_RATING_EXEMPT = None

PRICE_RAW = '€375,000'
PRICE = 375000
PRICE_BIG_RAW = '€2,750,000'
PRICE_BIG = 2750000
PRICE_NO_VALUE_RAW = '\n'
PRICE_NO_VALUE = None
PRICE_INVALID = None
PRICE_INVALID_RAW = 'INVALID'
PRICE_ON_APPLICATION_RAW = 'Price On Application'
PRICE_INVALID_EXCEPTION_MSG = r"Error .*pars.*price.*:'INVALID'"

QUICK_DETAILS_RAW_BED_FIRST = ['Number of beds is 3', 'Number of bathroom is 2']
QUICK_DETAILS_RAW_BATH_FIRST = ['Number of bathroom is 2', 'Number of beds is 3']
QUICK_DETAILS_RAW_ONLY_BED = ['Number of beds is 3']
QUICK_DETAILS_RAW_ONLY_BATH = ['Number of bathroom is 2']
BEDROOMS = 3
BEDROOMS_NO_VALUE = None
BATHROOMS = 2
BATHROOMS_NO_VALUE = None

FLOOR_AREA_RAW = ['\\n                                                    ',
                  '\\n                        '
                  '\\n                                                    ',
                  '\\n                            54 m',
                  '\\n                        '
                  '\\n                        '
                  '\\n                    ']
FLOOR_AREA = 54
FLOOR_AREA_DECIMAL_RAW = ['\\n                                                    ',
                          '\\n                        '
                          '\\n                                                    ',
                          '\\n                            50.3 m',
                          '\\n                        '
                          '\\n                        '
                          '\\n                    ']
FLOOR_AREA_DECIMAL = 50.3

MAIN_ADDRESS_RAW = "Apartment 12, Stewart Hall, Ryder's Row, Dublin 1, Dublin City Centre"
MAIN_ADDRESS = "Apartment 12, Stewart Hall, Ryder's Row, Dublin 1, Dublin City Centre"
MAIN_ADDRESS_SINGLE_RAW = 'SingleAdress'
MAIN_ADDRESS_NO_DISTRICT_DUN_LAOGHAIRE = '7 Crofton Terrace, Dun Laoghaire, South Co. Dublin'
MAIN_ADDRESS_NO_DISTRICT_MALAHIDE = '44 The Walk, Robswalls, Malahide, North Co. Dublin'
MAIN_ADDRESS_SECTOR = 'Dublin City Centre'
MAIN_ADDRESS_NO_DISTRICT_DUN_LAOGHAIRE_SECTOR = 'South Co. Dublin'
MAIN_ADDRESS_NO_DISTRICT_MALAHIDE_SECTOR = 'North Co. Dublin'
MAIN_ADDRESS_DISTRICT = 'Dublin 1'
MAIN_ADDRESS_REGION = "Ryder's Row"
MAIN_ADDRESS_NO_DISTRICT_DUN_LAOGHAIRE_REGION = 'Dun Laoghaire'
MAIN_ADDRESS_NO_DISTRICT_MALAHIDE_REGION = 'Malahide'

EIR_CODE_RAW = ['\n                            ', ' D04\xa0TD53\n                        ']
EIR_CODE = 'D04-TD53'
EIR_CODE_NO_VALUE_RAW = []
EIR_CODE_NO_VALUE = None

GEOLOCATION_RAW = 'https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=53.329523,-6.278734'
GEOLOCATION = '53.329523,-6.278734'

DESCRIPTION_RAW = ["\n                         A wonderful opportunity ", '\n',
                   '\nThis attractive double ', ", Palmerston Park, local ",
                   '\nSide entrance\n                    ',
                   'Make it stand out and get up to 15x more views']
DESCRIPTION = "A wonderful opportunity This attractive double , Palmerston Park," \
              " local Side entrance Make it stand out and get up to 15x more views"

STATISTICS_RAW = ['19.04.2020', '2914']
UPDATED_AT = '2020-04-19'
VIEWS = 2914

URL = 'url'

FULL_LINK_2 = 'http://site.com/link_2'

FULL_LINK_1 = 'http://site.com/link_1'

SHORT_LINK_1 = 'link_1'
SHORT_LINK_2 = 'link_2'

INITIAL_AREAS = "dublin-2,dublin-3"


@pytest.fixture
def daft_sale_used():
    return DaftSaleUsedSpider(INITIAL_AREAS)


@pytest.fixture
def response():
    result = Response(URL)
    result.request = Response(URL)
    return result


def test_daft_sale_used_spider_init(daft_sale_used):
    assert daft_sale_used.start_urls == [
        DAFT_ADDRESS + DUBLIN_CITY + PROPERTIES_FOR_SALE + INITIAL_AREAS]


@patch('web_scraper.spiders.Request')
def test_daft_sale_should_parse_property_cards(request_mock, daft_sale_used):
    mock_list_response = MagicMock()
    property1 = _generate_response_for_css_selector(SHORT_LINK_1)
    property2 = _generate_response_for_css_selector(SHORT_LINK_2)
    mock_list_response.css.return_value = [property1, property2]
    mock_list_response.urljoin.side_effect = [FULL_LINK_1, FULL_LINK_2]

    detailed_request_generator = daft_sale_used.parse(mock_list_response)

    results = [value for value in detailed_request_generator]
    assert len(results) == 2

    mock_list_response.css.assert_called_once_with(PROPERTY_CARD_SELECTOR)
    property1.css.assert_called_once_with(LINK_SELECTOR)
    property2.css.assert_called_once_with(LINK_SELECTOR)

    mock_list_response.urljoin.assert_has_calls([call(SHORT_LINK_1), call(SHORT_LINK_2)])

    request_mock.assert_has_calls([call(FULL_LINK_1, callback=daft_sale_used.parse_detailed_page),
                                   call(FULL_LINK_2, callback=daft_sale_used.parse_detailed_page)])


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_property_link(extractor, daft_sale_used, response):
    data_generator = daft_sale_used.parse_detailed_page(response)

    results = [value for value in data_generator]

    assert len(results) == 1
    assert results[0]['link'] == 'url'


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_property_type(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_property_type,
                             PROPERTY_TYPE, 'property_type')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_ber_rating(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_ber_rating,
                             BER_RATING, 'ber_rating')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_price(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_price,
                             PRICE, 'price')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_bedrooms(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_bedrooms,
                             BEDROOMS, 'bedrooms')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_bathrooms(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_bathrooms,
                             BATHROOMS, 'bathrooms')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_floor_area(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_floor_area,
                             FLOOR_AREA, 'floor_area_m2')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_main_address(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_main_address,
                             MAIN_ADDRESS, 'main_address')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_sector(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_sector,
                             MAIN_ADDRESS_SECTOR, 'sector')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_district(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_district,
                             MAIN_ADDRESS_DISTRICT, 'district')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_region(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_region,
                             MAIN_ADDRESS_DISTRICT, 'region')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_eir_code(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_eir_code,
                             MAIN_ADDRESS_DISTRICT, 'eir_code')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_geolocation(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_geolocation,
                             MAIN_ADDRESS_DISTRICT, 'geolocation')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_description(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_description,
                             DESCRIPTION, 'description')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_updated_at(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_updated_at,
                             UPDATED_AT, 'updated_at')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_views(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_views,
                             VIEWS, 'views')


def test_daft_extractor_should_extract_property_type():
    _assert_parsed_by_extractor(DaftExtractor.extract_property_type, PROPERTY_TYPE_SELECTOR,
                                PROPERTY_TYPE_RAW, PROPERTY_TYPE)


@pytest.mark.parametrize('raw_value, expected_value', [
    (BER_RATING_RAW, BER_RATING),
    (BER_RATING_RAW_SINGLE_CHAR, BER_RATING_SINGLE_CHAR),
    (BER_RATING_RAW_EXEMPT, BER_RATING_EXEMPT),
])
def test_daft_extractor_should_extract_ber_rating(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_ber_rating,
                                BER_RATING_IMAGE_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value, exception_msg', [
    (PRICE_RAW, PRICE, None),
    (PRICE_BIG_RAW, PRICE_BIG, None),
    (PRICE_NO_VALUE_RAW, PRICE_NO_VALUE, None),
    (PRICE_ON_APPLICATION_RAW, PRICE_NO_VALUE, None),
    (PRICE_INVALID_RAW, PRICE_INVALID, PRICE_INVALID_EXCEPTION_MSG),
])
def test_daft_extractor_should_extract_price(raw_value, expected_value, exception_msg):
    _assert_parsed_by_extractor(DaftExtractor.extract_price,
                                PRICE_SELECTOR, raw_value, expected_value, exception_msg)


@pytest.mark.parametrize('raw_value, expected_value', [
    (QUICK_DETAILS_RAW_BED_FIRST, BEDROOMS),
    (QUICK_DETAILS_RAW_BATH_FIRST, BEDROOMS),
    (QUICK_DETAILS_RAW_ONLY_BED, BEDROOMS),
    (QUICK_DETAILS_RAW_ONLY_BATH, BEDROOMS_NO_VALUE),
])
def test_daft_extractor_should_extract_bed_rooms(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_bedrooms,
                                QUICK_DETAILS_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (QUICK_DETAILS_RAW_BED_FIRST, BATHROOMS),
    (QUICK_DETAILS_RAW_BATH_FIRST, BATHROOMS),
    (QUICK_DETAILS_RAW_ONLY_BED, BATHROOMS_NO_VALUE),
    (QUICK_DETAILS_RAW_ONLY_BATH, BATHROOMS),
])
def test_daft_extractor_should_extract_bath_rooms(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_bathrooms,
                                QUICK_DETAILS_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (FLOOR_AREA_RAW, FLOOR_AREA),
    (FLOOR_AREA_DECIMAL_RAW, FLOOR_AREA_DECIMAL),
])
def test_daft_extractor_should_extract_floor_area(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_floor_area,
                                FLOOR_AREA_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (MAIN_ADDRESS_RAW, MAIN_ADDRESS),
    (MAIN_ADDRESS_SINGLE_RAW, MAIN_ADDRESS_SINGLE_RAW),
])
def test_daft_extractor_should_extract_main_address(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_main_address,
                                MAIN_ADDRESS_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (MAIN_ADDRESS_RAW, MAIN_ADDRESS_SECTOR),
    (MAIN_ADDRESS_SINGLE_RAW, None),
    (MAIN_ADDRESS_NO_DISTRICT_DUN_LAOGHAIRE, MAIN_ADDRESS_NO_DISTRICT_DUN_LAOGHAIRE_SECTOR),
    (MAIN_ADDRESS_NO_DISTRICT_MALAHIDE, MAIN_ADDRESS_NO_DISTRICT_MALAHIDE_SECTOR),
])
def test_daft_extractor_should_extract_sector(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_sector,
                                MAIN_ADDRESS_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (MAIN_ADDRESS_RAW, MAIN_ADDRESS_DISTRICT),
    (MAIN_ADDRESS_SINGLE_RAW, None),
    (MAIN_ADDRESS_NO_DISTRICT_DUN_LAOGHAIRE, None),
    (MAIN_ADDRESS_NO_DISTRICT_MALAHIDE, None),
])
def test_daft_extractor_should_extract_district(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_district,
                                MAIN_ADDRESS_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (MAIN_ADDRESS_RAW, MAIN_ADDRESS_REGION),
    (MAIN_ADDRESS_SINGLE_RAW, None),
    (MAIN_ADDRESS_NO_DISTRICT_DUN_LAOGHAIRE, MAIN_ADDRESS_NO_DISTRICT_DUN_LAOGHAIRE_REGION),
    (MAIN_ADDRESS_NO_DISTRICT_MALAHIDE, MAIN_ADDRESS_NO_DISTRICT_MALAHIDE_REGION),
])
def test_daft_extractor_should_extract_region(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_region,
                                MAIN_ADDRESS_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (EIR_CODE_RAW, EIR_CODE),
    (EIR_CODE_NO_VALUE_RAW, EIR_CODE_NO_VALUE),
])
def test_daft_extractor_should_extract_eir_code(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_eir_code,
                                EIR_CODE_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (GEOLOCATION_RAW, GEOLOCATION),
])
def test_daft_extractor_should_extract_geolocation(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_geolocation,
                                STREET_VIEW_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (DESCRIPTION_RAW, DESCRIPTION),
])
def test_daft_extractor_should_extract_description(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_description,
                                DESCRIPTION_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (STATISTICS_RAW, UPDATED_AT),
])
def test_daft_extractor_should_extract_updated_at(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_updated_at,
                                STATISTICS_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (STATISTICS_RAW, VIEWS),
])
def test_daft_extractor_should_extract_views(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_views,
                                STATISTICS_SELECTOR, raw_value, expected_value)


def _generate_response_for_css_selector(result: Any):
    response = MagicMock(Response)
    css_result = MagicMock()

    css_result.get.return_value = result
    css_result.getall.return_value = result
    response.css.return_value = css_result

    return response


def _assert_extractor_called(daft_sale_used, response, extractor_function, extractor_result,
                             property_name) -> None:
    extractor_function.side_effect = [extractor_result]
    data_generator = daft_sale_used.parse_detailed_page(response)

    results = [value for value in data_generator]

    assert len(results) == 1
    assert results[0][property_name] == extractor_result

    extractor_function.assert_called_once_with(response)


def _assert_parsed_by_extractor(extractor, selector, raw_value, expected_value,
                                expected_exception_regex=None):
    response = _generate_response_for_css_selector(raw_value)

    if not expected_exception_regex:
        result = extractor(response)
        assert result == expected_value
    else:
        with pytest.raises(ExtractorException, match=expected_exception_regex):
            extractor(response)

    response.css.assert_called_once_with(selector)
