"""Match company names via Google Finance
"""
import random
import time

import requests
from lxml import html as HTMLParser

from .base import BaseNameMatcher, CompanyUnderline
from ._utils import get_logger


class GoogleFinanceNameMatcher(  # pylint: disable=too-few-public-methods
        BaseNameMatcher):
    def __init__(self):
        super(GoogleFinanceNameMatcher, self).__init__()
        self.base_url = 'https://finance.google.com/finance'

    def _parse_google_finance_response(self, page_content):
        symbols = []
        primary_sel = (
            '#appbar > div.elastic > div.appbar-center > '
            'div.appbar-snippet-primary > span'
        )
        secondary_sel = (
            '#appbar > div.elastic > div.appbar-center > '
            'div.appbar-snippet-secondary > span'
        )
        others_sel = ('.gf-table.company_results > tr.snippet')
        parsed = HTMLParser.fromstring(page_content)
        com_name_elems = parsed.cssselect(primary_sel)
        ti_elems = parsed.cssselect(secondary_sel)
        if com_name_elems:
            ticker = ti_elems[0].text.strip().lstrip('(').rstrip(')')
            symbols.append((
                com_name_elems[0].text,
                ticker.split(':')[0], ticker.split(':')[1]
            ))
        else:
            rows = parsed.cssselect(others_sel)
            for row in rows:
                rec = [
                    ''.join(el.itertext()).strip()
                    for el in row.cssselect('td')
                ]
                symbols.append((rec[0], rec[1], rec[2]))
        return symbols

    def _find_stock_for_name(self, name, retry=5, sleep=30):
        params = {'q': name}
        headers = self._get_headers()
        symbols = []
        for retry_num in range(retry):
            try:
                res = requests.get(
                    self.base_url, headers=headers, params=params
                )
                symbols = self._parse_google_finance_response(res.content)
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
        sleep = kwargs.pop('sleep', 30)
        for name in names:
            symbols = self._find_stock_for_name(
                name, retry=retry, sleep=sleep,
            )
            ret[name] = []
            for symbol in symbols:
                ret[name].append(
                    (symbol[0], CompanyUnderline(
                        ticker=symbol[2], google_exch=symbol[1]
                    ), {})
                )
        return ret
