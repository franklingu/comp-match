"""Collection of util functions
"""
import os
import logging
import time
import random
try:
    import simplejson as json
except ImportError:
    import json

import requests
from lxml import html as HTMLParser


__all__ = [
    'find_google_exchange', 'find_yahoo_exchange',
    'find_country_for_exchange', 'find_country_repr',
    'get_logger',
]


class ResourceManager(object):
    def __init__(self, exchange_path=None, country_path=None):
        super(ResourceManager, self).__init__()
        dirpath = os.path.dirname(os.path.abspath(__file__))
        if exchange_path is None:
            exchange_path = os.path.join(
                dirpath, '../resources/exchanges.json'
            )
        if country_path is None:
            country_path = os.path.join(
                dirpath, '../resources/iso_countries.json'
            )
        self.exchange_path = exchange_path
        self.country_path = country_path
        with open(self.exchange_path, 'r') as ifile:
            raw_exchanges = json.load(ifile)['exchanges']
            exchanges = {}
            google_exches = {}
            yahoo_exches = {}
            for exch in raw_exchanges:
                exchanges[exch['exchange']] = exch
                if exch.get('google_exch'):
                    google_exches[exch['google_exch']] = exch
                if exch.get('yahoo_exch'):
                    yahoo_exches[exch['yahoo_exch']] = exch
            self.exchanges = exchanges
            self.google_exches = google_exches
            self.yahoo_exches = yahoo_exches
        with open(self.country_path, 'r') as ifile:
            raw_countries = json.load(ifile)['3166-1']
            countries = {}
            for country in raw_countries:
                countries[country['name']] = country
            self.countries = countries

    def find_exchange_by(self, **kwargs):
        """match to raw exchange dict by given criteria
        """
        if 'exchange' in kwargs:
            return self.exchanges.get(kwargs['exchange'])
        elif 'google_exch' in kwargs:
            return self.google_exches.get(kwargs['google_exch'])
        elif 'yahoo_exch' in kwargs:
            return self.yahoo_exches.get(kwargs['yahoo_exch'])
        else:
            raise ValueError('Unknown exchange type for matching')

    def find_country_by(self, **kwargs):
        """match to raw country dict by given criteria
        """
        if kwargs['country'] in self.countries:
            return self.countries[kwargs['country']]
        return None


resource_manager = ResourceManager()


def find_google_exchange(google_exch):
    """Find official exchange name for given google_exch
    """
    match = resource_manager.find_exchange_by(google_exch=google_exch)
    if not match:
        return None
    return match['exchange']


def find_yahoo_exchange(yahoo_exch):
    """Find official exchange name for given yahoo_exch
    """
    match = resource_manager.find_exchange_by(yahoo_exch=yahoo_exch)
    if not match:
        return None
    return match['exchange']


def find_country_for_exchange(exchange):
    """Find country 2-letter short code or name for given exchange

    If iso-3166 short code is available, return short code; other matched
    country name will be returned
    """
    match = resource_manager.find_exchange_by(exchange=exchange)
    if not match:
        return None
    country_match = resource_manager.find_country_by(country=match['country'])
    if not country_match:
        return match['country']
    return country_match['alpha_2']


def find_country_repr(country):
    """Find country 2-letter short code or return as it is
    """
    country_match = resource_manager.find_country_by(country=country)
    if not country_match:
        return country
    return country_match['alpha_2']


def get_logger():
    """Return internal logger
    """
    return logging.getLogger('comp_match')


def get_exchanges_from_remote(retry=5):
    """Get exchanges from wikiinvest
    """
    link = 'http://www.wikinvest.com/wiki/List_of_Stock_Exchanges'
    headers = {
        'Accept': (
            'text/html,application/xhtml+xml,application/xml;'
            'q=0.9,image/webp,*/*;q=0.8'
        ),
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
        'User-Agent': (
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Ubuntu Chromium/52.0.2743.116 '
            'Chrome/52.0.2743.116 Safari/537.36'
        )
    }
    query_sel = '//table//td/b[contains(text(), "Google Finance")]/../../..'
    data = []
    for retry_num in range(retry):
        try:
            res = requests.get(link, headers=headers)
            parsed = HTMLParser.fromstring(res.content)
            tbls = parsed.xpath(query_sel)
            for tbl in tbls:
                country = None
                header = None
                for tr in tbl.xpath('tr'):
                    row = [
                        ''.join(td.itertext()).strip()
                        for td in tr.xpath('td')
                    ]
                    if header is None:
                        header = row
                        continue
                    yahoo_exch = row[4]
                    google_exch = row[3]
                    exchange = row[1]
                    if row[0]:
                        country = row[0]
                    data.append({
                        'country': country,
                        'exchange': exchange,
                        'google_exch': google_exch,
                        'yahoo_exch': yahoo_exch
                    })
            return data
        except Exception as err:
            get_logger().debug(
                'Exception during requesting exchanges: %s', str(err)
            )
            if retry_num == retry - 1:
                raise
            time.sleep(random.random() * 5)
    return data


def get_google_finance_exchanges():
    try:
        from selenium import webdriver
    except ImportError:
        print('selenium is required')
        return None
    driver = None
    try:
        driver = webdriver.Firefox()
        driver.get('https://finance.google.com')
        # click stock screen item
        driver.find_elements_by_css_selector('#navmenu > li')[-2].click()
        time.sleep(3)
        data = {}
        # iterate by countries now
        country_elems = driver.find_elements_by_css_selector(
            '.id-regionselect option'
        )
        for country_elem in country_elems:
            country_code = country_elem.get_attribute('value').upper()
            country_name = country_elem.text
            country_elem.click()
            exch_elems = driver.find_elements_by_css_selector(
                '#exchangeselect option'
            )
            for exch_elem in exch_elems:
                google_exch = exch_elem.get_attribute('value')
                # ignore empty or allexchanges options
                if google_exch is None or google_exch == 'AllExchanges':
                    continue
                fullname = exch_elem.text
                fullname = fullname[:fullname.index('(')].strip()
                data[google_exch] = (fullname, country_name, country_code)
    except Exception:
        if driver is not None:
            driver.quit()
    return data
