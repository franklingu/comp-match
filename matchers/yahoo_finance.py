"""Match company names via Yahoo Finance
"""
import random
import time

import requests

from .base import BaseNameMatcher, CompanyUnderline
from ._utils import get_logger


class YahooFinanceNameMatcher(BaseNameMatcher):
    def __init__(self):
        super(YahooFinanceNameMatcher, self).__init__()
        self.base_url = 'http://autoc.finance.yahoo.com/autoc'
        self.ua_reprs = [
            (
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0)'
                ' Gecko/20100101 Firefox/46.0'
            ),
            (
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                ' (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.120'
                ' Chrome/37.0.2062.120 Safari/537.36'
            ),
        ]

    def _get_headers(self):
        ua = self.ua_reprs[random.randint(0, len(self.ua_reprs) - 1)]
        acc = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        return {
            'User-Agent': ua,
            'Accept': acc,
            'Accept-Language': 'en-US,en;q=0.5',
        }

    def _find_stock_for_name(self, name, retry=5):
        MAX_RETRY = retry
        params = {'query': name, 'lang': 'en-US'}
        headers = self._get_headers()
        symbols = []
        for retry_num in range(MAX_RETRY):
            try:
                res = requests.get(
                    self.base_url, headers=headers, params=params
                )
                data = res.json()
                for result in data['ResultSet']['Result']:
                    ticker = result.get('symbol', '').split('.')[0]
                    exch = ''
                    if len(result.get('symbol', '').split('.')) >= 2:
                        exch = result.get('symbol', '').split('.')[1]
                    symbols.append((
                        result.get('name', ''),
                        ticker, exch,
                        (result.get('exch', ''), result.get('exchDisp', ''))
                    ))
                break
            except Exception as err:
                get_logger().debug(
                    'Error happened via querying Yahoo Finance: %s', str(err)
                )
                symbols = []
                if retry_num == MAX_RETRY - 1:
                    raise
                else:
                    time.sleep(random.random())
        return symbols

    def match_by(self, names, retry=5):
        """Match by name via Yahoo Finance

        Params:
            names: a company name or a list of company names

        Returns:
            dict of  orig_name: (mapped legal name, underline, addon info dict)
        """
        if isinstance(names, str):
            names = [names]
        ret = {}
        names = set(names)
        for name in names:
            symbols = self._find_stock_for_name(name, retry=retry)
            if symbols:
                ret[name] = [
                    (symbol[0], CompanyUnderline(
                        ticker=symbol[2], Yahoo_exch=symbol[1]
                    ), {'exchange': symbol[3]}) for symbol in symbols
                ]
            else:
                ret[name] = None
        return ret
