import json
import re
from typing import Generator, Any, Dict, List, Optional

from scrapy import Spider, Request
from scrapy.http import Response

DUBLIN_CITY_SECTOR = 'Dublin City'

BER_RATING_EXEMPT = 'EXEMPT'

PROPERTY_CARD_SELECTOR = ".PropertyCardContainer__container "

DAFT_ADDRESS = "https://www.daft.ie"
DUBLIN_CITY = "/dublin-city"
PROPERTIES_FOR_SALE = "/property-for-sale"

LINK_SELECTOR = ".PropertyInformationCommonStyles__addressCopy--link::attr(href)"
PROPERTY_TYPE_SELECTOR = ".QuickPropertyDetails__propertyType::text"
MAIN_ADDRESS_SELECTOR = '.PropertyMainInformation__address::text'
BER_RATING_IMAGE_SELECTOR = '.PropertyImage__berImage::attr(src)'
PRICE_SELECTOR = '.PropertyInformationCommonStyles__costAmountCopy::text'
QUICK_DETAILS_SELECTOR = ".PropertyInformationCommonStyles__quickPropertyDetailsContainer " \
                         ".QuickPropertyDetails__iconContainer img::attr(alt)"
FLOOR_AREA_SELECTOR = '.PropertyOverview__propertyOverviewDetails::text'
EIR_CODE_SELECTOR = '.PropertyMainInformation__eircode::text'
STREET_VIEW_SELECTOR = '.MapActions #LaunchStreet::attr(href)'
DESCRIPTION_SELECTOR = '.PropertyDescription__propertyDescription::text'
STATISTICS_SELECTOR = '.PropertyStatistics__iconsContainer .PropertyStatistics__iconData::text'


class DaftSaleUsedSpider(Spider):  # type: ignore
    name = "DaftSaleUsed"

    def __init__(self,
                 areas_string: Optional[str] = None,
                 min_price: Optional[int] = None,
                 max_price: Optional[int] = None,
                 min_beds: Optional[int] = None,
                 max_beds: Optional[int] = None,
                 ) -> None:
        super(DaftSaleUsedSpider, self).__init__()

        initial_url = DAFT_ADDRESS + DUBLIN_CITY + PROPERTIES_FOR_SALE

        if areas_string:
            initial_url += "/" + areas_string

        url_args = "/?ad_type=sale"

        url_args += DaftSaleUsedSpider._url_arg('mnp', min_price)
        url_args += DaftSaleUsedSpider._url_arg('mxp', max_price)
        url_args += DaftSaleUsedSpider._url_arg('mnb', min_beds)
        url_args += DaftSaleUsedSpider._url_arg('mxb', max_beds)

        self.start_urls = [initial_url + url_args]

    def parse(self, response: Response) -> Generator[Request, None, None]:
        for daft_property in response.css(PROPERTY_CARD_SELECTOR):
            detailed_link = response.urljoin(daft_property.css(LINK_SELECTOR).get())
            yield Request(detailed_link, callback=self.parse_detailed_page)

    def parse_detailed_page(self, response: Response) -> Generator[Dict[str, Any], None, None]:
        yield {
            'link': response.request.url,
            'property_type': DaftExtractor.extract_property_type(response),
            'ber_rating': DaftExtractor.extract_ber_rating(response),
            'price': DaftExtractor.extract_price(response),
            'bedrooms': DaftExtractor.extract_bedrooms(response),
            'bathrooms': DaftExtractor.extract_bathrooms(response),
            'floor_area_m2': DaftExtractor.extract_floor_area(response),
            'main_address': DaftExtractor.extract_main_address(response),
            'sector': DaftExtractor.extract_sector(response),
            'district': DaftExtractor.extract_district(response),
            'region': DaftExtractor.extract_region(response),
            'eir_code': DaftExtractor.extract_eir_code(response),
            'geolocation': DaftExtractor.extract_geolocation(response),
            'description': DaftExtractor.extract_description(response),
            'updated_at': DaftExtractor.extract_updated_at(response),
            'views': DaftExtractor.extract_views(response),
        }

    @staticmethod
    def _url_arg(arg_name: str, arg_value: Any) -> str:
        if arg_value:
            return f'&s%5B{arg_name}%5D={arg_value}'
        else:
            return ''


class DaftExtractor:
    _ber_rating_regex = re.compile("^.*/\\w+_(\\w+)\\..*$")
    _price_replace_regex = re.compile("[^\\d]")
    _quick_details_regex = re.compile("^Number.* (\\w+) is .*(\\d+)$")
    _FLOOR_AREA_REGEX = re.compile(".*\\s+(\\d+(\\.\\d+)?).* m")
    _EIR_CODE_REGEX = re.compile("\\s+(\\w{3}).(\\w{4})")
    _UPDATED_AT_REGEX = re.compile("^(\\d{1,2}).(\\d{1,2}).(\\d{4})$")
    _ONLY_NUMBERS_REGEX = re.compile("^\\d+$")

    @staticmethod
    def extract_property_type(response: Response) -> str:
        result = str(DaftExtractor._extract_css_selector(response, PROPERTY_TYPE_SELECTOR))
        return result.strip()

    @staticmethod
    def extract_ber_rating(response: Response) -> Optional[str]:
        ber_rating_image_url = str(DaftExtractor._extract_css_selector(
            response, BER_RATING_IMAGE_SELECTOR))
        result = None
        if ber_rating_image_url:
            if matcher := DaftExtractor._ber_rating_regex.match(ber_rating_image_url):
                ber_rating = matcher.group(1).upper()
                if BER_RATING_EXEMPT not in ber_rating:
                    result = ber_rating
        return result

    @staticmethod
    def extract_price(response: Response) -> Optional[int]:
        price_text = str(DaftExtractor._extract_css_selector(response, PRICE_SELECTOR))
        result = None
        if price_text:
            try:
                result = int(DaftExtractor._price_replace_regex.sub("", price_text))
            except ValueError as e:
                if price_text.strip() and 'APPLICATION' not in price_text.upper():
                    raise ExtractorException('Error parsing price', price_text, e)
        return result

    @staticmethod
    def extract_bedrooms(response: Response) -> Optional[int]:
        return DaftExtractor._extract_quick_details(response, 'beds')

    @staticmethod
    def extract_bathrooms(response: Response) -> Optional[int]:
        return DaftExtractor._extract_quick_details(response, 'bathroom')

    @staticmethod
    def extract_floor_area(response: Response) -> Optional[float]:
        floor_area_raw = DaftExtractor._extract_css_selector(response, FLOOR_AREA_SELECTOR, True)
        floor_area = None
        for floor_area_text in floor_area_raw:
            if matcher := DaftExtractor._FLOOR_AREA_REGEX.match(floor_area_text):
                floor_area = float(matcher.group(1))
        return floor_area

    @staticmethod
    def extract_main_address(response: Response) -> str:
        result = str(DaftExtractor._extract_css_selector(response, MAIN_ADDRESS_SELECTOR))
        return result.strip()

    @staticmethod
    def extract_sector(response: Response) -> Optional[str]:
        main_address_parts = str(DaftExtractor._extract_css_selector(
            response, MAIN_ADDRESS_SELECTOR)).split(',')
        result = None
        if len(main_address_parts) > 1:
            result = main_address_parts[-1].strip()
        return result

    @staticmethod
    def extract_district(response: Response) -> Optional[str]:
        main_address_parts = str(DaftExtractor._extract_css_selector(
            response, MAIN_ADDRESS_SELECTOR)).split(',')
        result = None
        if len(main_address_parts) > 2 and DUBLIN_CITY_SECTOR in main_address_parts[-1]:
            result = main_address_parts[-2].strip()
        return result

    @staticmethod
    def extract_region(response: Response) -> Optional[str]:
        main_address_parts = str(DaftExtractor._extract_css_selector(
            response, MAIN_ADDRESS_SELECTOR)).split(',')
        result = None
        if len(main_address_parts) > 2 and DUBLIN_CITY_SECTOR in main_address_parts[-1]:
            result = main_address_parts[-3].strip()
        elif len(main_address_parts) > 2:
            result = main_address_parts[-2].strip()
        return result

    @staticmethod
    def extract_eir_code(response: Response) -> Optional[str]:
        eir_code_raw = DaftExtractor._extract_css_selector(response, EIR_CODE_SELECTOR, True)
        eir_code = None
        for eir_code_text in eir_code_raw:
            if matcher := DaftExtractor._EIR_CODE_REGEX.match(eir_code_text):
                eir_code = matcher.group(1) + '-' + matcher.group(2)
        return eir_code

    @staticmethod
    def extract_geolocation(response: Response) -> Optional[str]:
        street_view_link = DaftExtractor._extract_css_selector(response, STREET_VIEW_SELECTOR)
        result = None
        if street_view_link:
            raw_coordinates = street_view_link.split('=')[-1]
            result = raw_coordinates
        return result

    @staticmethod
    def extract_description(response: Response) -> str:
        description_text = DaftExtractor._extract_css_selector(response, DESCRIPTION_SELECTOR, True)
        result = ""
        for line in description_text:
            if line_text := line.strip():
                result += line_text + " "
        return result.strip()

    @staticmethod
    def extract_updated_at(response: Response) -> Optional[str]:
        statistics_raw = DaftExtractor._extract_css_selector(response, STATISTICS_SELECTOR, True)
        updated_at = None
        for statistics_entry in statistics_raw:
            if matcher := DaftExtractor._UPDATED_AT_REGEX.match(statistics_entry):
                updated_at = matcher.group(3) + '-' + matcher.group(2) + '-' + matcher.group(1)
                break
        return updated_at

    @staticmethod
    def extract_views(response: Response) -> Optional[int]:
        statistics_raw = DaftExtractor._extract_css_selector(response, STATISTICS_SELECTOR, True)
        views = None
        for statistics_entry in statistics_raw:
            if DaftExtractor._ONLY_NUMBERS_REGEX.match(statistics_entry):
                views = int(statistics_entry)
                break
        return views

    @staticmethod
    def _extract_css_selector(response: Response, selector: str, get_all: bool = False) -> Any:
        if not get_all:
            return response.css(selector).get()
        else:
            return response.css(selector).getall()

    @staticmethod
    def _extract_quick_details(response: Response, detail_type: str) -> Optional[int]:
        quick_details = DaftExtractor._extract_css_selector(
            response, QUICK_DETAILS_SELECTOR, True)
        detail_value = None
        if quick_details:
            for detail in quick_details:
                if matcher := DaftExtractor._quick_details_regex.match(detail):
                    if matcher.group(1) == detail_type:
                        detail_value = int(matcher.group(2))
        return detail_value


class ExtractorException(Exception):
    def __init__(self, error_msg: str, raw_value: str, error: Any):
        self.message = f'{error_msg}:\'{raw_value}\' - {error}'

    def __str__(self) -> str:
        return self.message
