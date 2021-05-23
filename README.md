# Web Scraper

## Description
Some toy tools to scrape some **irish** web sites and get some test data

## How to run it:
PYTHONPATH="PATH_TO_PROJECT/web_scraper:${PYTHONPATH}" python bin/web-scraper houses-for-sale --locations dublin-4-dublin dublin-6-dublin --min-price 100000 --max-price 300000

## How to run the tests:
PYTHONPATH="PATH_TO_PROJECT/web_scraper:${PYTHONPATH}" pytest -vv --cov=web_scraper

## Available Scrapers

### Houses for sale(houses_for_sale)

Scraps sites(only daft at the moment) for used houses for sale

#### Parameters:
* **locations**: areas that are being scraped as shown in daft.ie site, comes from the `location` parameters.
On the url:
  https://www.daft.ie/property-for-sale/ireland?location=dublin-4-dublin&location=dublin-6-dublin&salePrice_from=100000&salePrice_to=350000&numBeds_from=2
    areas string would be 'dublin-4-dublin dublin-6-dublin'.

* **min-price**: minimum price for the property in euros. I.e: `100000` would only show properties more expensive than 100k.
* **max-price**: maximum price for the property in euros. I.e: `350000` would only show properties that are cheaper than 350k.
* **min-bed**: minimum beds. I.e: `2` would only show properties with at least 2 beds.
* **max-price**: maximum beds. I.e: `4` would only show properties with less than 4 beds.


