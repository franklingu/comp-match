"""Match company names via Google Finance
"""
import random
import time
try:
    import simplejson as json
except ImportError:
    import json

import requests

from .base import BaseNameMatcher, CompanyUnderline
from ._utils import get_logger


class GoogleFinanceNameMatcher(  # pylint: disable=too-few-public-methods
        BaseNameMatcher):
    """Match name to stock ticker via Google Finance
    """
    AGENT = 'google_finance'

    def __init__(self):
        super(GoogleFinanceNameMatcher, self).__init__()
        self.base_url = 'https://www.google.com/complete/search'

    def _parse_google_finance_response(  # pylint: disable=no-self-use
            self, name, page_content):
        symbols = []
        try:
            parsed = json.loads(page_content)
        except ValueError:
            raise
        except TypeError:
            parsed = json.loads(page_content.decode('utf-8'))
        if (not isinstance(parsed, list) or not parsed or parsed[0] != name
                or len(parsed) < 2):
            raise ValueError('Google response does not seem normal')
        for candidate in parsed[1]:
            if len(candidate) < 4 or not isinstance(candidate[3], dict):
                continue
            ticker = candidate[3].get('t', '')
            google_exch = candidate[3].get('x', '')
            mapped_name = candidate[3].get('c', '')
            if not ticker or not google_exch:
                continue
            symbols.append((mapped_name, ticker, google_exch))
        return symbols

    def _find_stock_for_name(self, name, retry=5, sleep=30):
        params = {
            'client': 'finance-immersive',
            'q': name,
            'xhr': 't',
        }
        headers = self._get_headers()
        symbols = []
        for retry_num in range(retry):
            try:
                res = requests.get(
                    self.base_url, headers=headers, params=params
                )
                symbols = self._parse_google_finance_response(
                    name, res.content
                )
                break
            except Exception as err:  # pylint: disable=broad-except
                get_logger().debug(
                    'Error happened when querying Google Finance: %s', str(err)
                )
                symbols = []
                if retry_num == retry - 1:
                    continue
                else:
                    time.sleep(random.random() * sleep + retry_num * sleep)
        return symbols

    def _match_by(self, names, **kwargs):
        ret = {}
        retry = kwargs.pop('retry', 5)
        sleep = int(kwargs.pop('sleep', 30))
        for name in names:
            symbols = self._find_stock_for_name(
                name, retry=retry, sleep=sleep,
            )
            ret[name] = []
            for symbol in symbols:
                ret[name].append(
                    (symbol[0], CompanyUnderline(
                        ticker=symbol[1], google_exch=symbol[2]
                    ), {})
                )
        return ret
