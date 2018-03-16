"""match company names to tickers
"""
import random
import time

import requests
from lxml import etree

from ._utils import get_logger
from .base import BaseNameMatcher, CompanyUnderline


class OpenCalaisNameMatcher(  # pylint: disable=too-few-public-methods
        BaseNameMatcher):
    """Match company names to underlines via OpenCalais
    """
    def __init__(self, access_token=None):
        super(OpenCalaisNameMatcher, self).__init__()
        if access_token is None:
            access_token = '2Uqpdme4VlbUp46wQYxGJoGcw1GpPFpW'
        self.access_token = access_token

    def _get_headers(self):
        return {
            'X-AG-Access-Token': self.access_token,
            'Content-Type': 'text/raw',
            'outputformat': 'xml/rdf'
        }

    def _match_by(self, names, **kwargs):
        retry = kwargs.pop('retry', 5)
        sleep = kwargs.pop('sleep', 30)
        end, curr, step = len(names), 0, 50
        ret = {}
        while curr < end:
            range_end = curr + step if curr + step < end else end
            curr_names = names[curr:range_end]
            match_res = self._match_for_names(
                curr_names, retry=retry, sleep=sleep
            )
            if match_res:
                ret.update(match_res)
            curr = range_end
        return ret

    def _match_for_names(self, names, retry=5, sleep=30):
        content = ''.join(
            ('{} is a public company\r\n').format(name) for name in names
        ).encode('utf-8')
        link = 'https://api.thomsonreuters.com/permid/calais'
        for retry_num in range(retry):
            try:
                res = requests.post(
                    link, data=content, headers=self._get_headers(), timeout=80
                )
                res_content = res.content
                break
            except Exception as err:  # pylint: disable=broad-except
                get_logger().debug(
                    'Exception during requesting opencalais: %s', str(err)
                )
                if retry_num == retry - 1:
                    pass
                else:
                    time.sleep(random.random() * sleep + sleep * retry_num)
        raw_matches = self._process_rdf_response(res_content)
        ret_data = {}
        for name, raw_match in raw_matches.items():
            orig_name, legal_name, ric, ticker, permid, score = raw_match
            ret_data[orig_name] = [(
                legal_name,
                self._match_to_underline(
                    ticker, permid, retry=retry, sleep=sleep
                ),
                {'score': score, 'ric': ric}
            )]
        return ret_data

    def _process_rdf_response(self, res_content):
        """Parse rdf file from open calais
        """
        parsed = etree.parse(res_content)
        rdf = parsed.getroot()
        match = {}
        match_top = {}
        top_most_type = (
            'http://s.opencalais.com/1/type/er/TopmostPublicParentCompany'
        )
        raw = {}
        raw_top = {}
        descs = rdf.xpath('rdf:Description', namespaces=rdf.nsmap)
        names = [
            './c:exact', './c:name', './c:primaryric', './c:ticker',
            './c:permid', './c:score'
        ]
        for desc in descs:
            subjs = desc.xpath(
                './c:subject/@rdf:resource', namespaces=rdf.nsmap
            )
            rtype = desc.xpath(
                './rdf:type/@rdf:resource', namespaces=rdf.nsmap
            )
            if not subjs:
                continue
            else:
                # take only the first subject
                subj = subjs[0]
                if not subj.startswith('http://d.opencalais.com/comphash'):
                    continue
            if subj not in raw:
                raw[subj] = {}
                raw_top[subj] = {}
            for xp in names:
                elems = desc.xpath(xp, namespaces=rdf.nsmap)
                if elems:
                    if rtype and rtype[0] == top_most_type:
                        raw_top[subj][xp] = elems[0].text
                    else:
                        raw[subj][xp] = elems[0].text
        for subj, elem in raw.items():
            if not elem:
                continue
            row = [elem.get(name, '') for name in names]
            match[elem['./c:exact']] = row
        for subj, elem in raw_top.items():
            if not elem:
                continue
            row = [elem.get(name, '') for name in names]
            raw_elem = raw.get(subj)
            if not raw_elem:
                continue
            match_top[raw_elem['./c:exact']] = row
        ret = {}
        ret.update(match_top)
        ret.update(match)
        return ret

    def _match_to_underline(self, ticker, permid, retry=5, sleep=30):
        link = 'https://permid.org/api/mdaas/getEntityById/{}'.format(permid)
        headers = self._get_headers()
        del headers['Content-Type']
        del headers['outputformat']
        for retry_num in range(retry):
            try:
                res = requests.post(
                    link, headers=headers, timeout=80
                )
                res_obj = res.json()
                for quote in res_obj['mainQuoteId.mdaas']:
                    mic = quote.get('Primary Mic', [''])[0]
                    underline = CompanyUnderline(ticker=ticker, mic=mic)
                    return underline
            except Exception as err:  # pylint: disable=broad-except
                get_logger().debug(
                    'Exception during requesting opencalais: %s', str(err)
                )
                if retry_num == retry - 1:
                    pass
                else:
                    time.sleep(random.random() * sleep + sleep * retry_num)
