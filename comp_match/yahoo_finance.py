"""Match company names via Yahoo Finance
"""
import random
import time

import requests

from .base import BaseNameMatcher, CompanyUnderline
from ._utils import get_logger


class YahooFinanceNameMatcher(  # pylint: disable=too-few-public-methods
        BaseNameMatcher):
    def __init__(self):
        super(YahooFinanceNameMatcher, self).__init__()
        self.base_url = 'http://autoc.finance.yahoo.com/autoc'

    def _find_stock_for_name(  # pylint: disable=too-many-locals
            self, name, retry=5, sleep=30):
        params = {'query': name, 'lang': 'en-US'}
        symbols = []
        for retry_num in range(retry):
            try:
                res = requests.get(
                    self.base_url, headers=self._get_headers(), params=params
                )
                data = res.json()
                for result in data['ResultSet']['Result']:
                    ticker = result.get('symbol', '').split('.')[0]
                    # change A/B share representation
                    ticker = ticker.replace('-', '.')
                    type_desc = result.get('typeDisp', '')
                    if type_desc != 'Equity':
                        continue
                    yahoo_exch = ''
                    if len(result.get('symbol', '').split('.')) > 1:
                        yahoo_exch = '.' + result.get(
                            'symbol', ''
                        ).split('.')[1]
                        country = None
                    else:
                        country = 'US'
                    symbols.append((
                        result.get('name', ''),
                        ticker,
                        yahoo_exch,
                        country,
                        result.get('exch', ''),
                        result.get('exchDisp', '')
                    ))
                break
            except Exception as err:  # pylint: disable=broad-except
                get_logger().debug(
                    'Error happened via querying Yahoo Finance: %s', str(err)
                )
                symbols = []
                if retry_num == retry - 1:
                    continue
                else:
                    time.sleep(random.random() * sleep + retry_num * sleep)
        return symbols

    def _match_by(self, names, **kwargs):
        retry = kwargs.pop('retry', 5)
        sleep = kwargs.pop('sleep', 30)
        ret = {}
        for name in names:
            symbols = self._find_stock_for_name(name, retry=retry, sleep=sleep)
            ret[name] = []
            for symbol in symbols:
                ret[name].append((
                    symbol[0],
                    CompanyUnderline(
                        ticker=symbol[1],
                        yahoo_exch=symbol[2],
                        country_code=symbol[3]
                    ),
                    {'exch': symbol[4], 'exch_desc': symbol[5]}
                ))
        return ret
