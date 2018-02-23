"""Match company names via Google Finance
"""
import random
import time

import requests
from lxml import html as HTMLParser

from .base import BaseNameMatcher, CompanyUnderline
from ._utils import get_logger


class GoogleFinanceNameMatcher(BaseNameMatcher):
    def __init__(self):
        super(GoogleFinanceNameMatcher, self).__init__()
        self.base_url = 'https://www.google.com/finance'
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
        params = {'q': name}
        headers = self._get_headers()
        primary_sel = (
            '#appbar > div.elastic > div.appbar-center > '
            'div.appbar-snippet-primary > span'
        )
        secondary_sel = (
            '#appbar > div.elastic > div.appbar-center > '
            'div.appbar-snippet-secondary > span'
        )
        others_sel = ('.gf-table.company_results > tr.snippet')
        symbols = []
        for retry_num in range(MAX_RETRY):
            try:
                res = requests.get(
                    self.base_url, headers=headers, params=params
                )
                parsed = HTMLParser.fromstring(res.content)
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
                break
            except Exception as err:
                get_logger().debug(
                    'Error happened via querying Google Finance: %s', str(err)
                )
                symbols = []
                if retry_num == MAX_RETRY - 1:
                    raise
                else:
                    time.sleep(random.random())
        return symbols

    def match_by(self, names, retry=5):
        """Match by name via Google Finance

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
                        ticker=symbol[2], google_exch=symbol[1]
                    ), {}) for symbol in symbols
                ]
            else:
                ret[name] = None
        return ret
