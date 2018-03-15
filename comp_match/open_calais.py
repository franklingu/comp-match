"""match company names to tickers
"""
import requests
from lxml import etree

from .._common import _get_internal_logger
from .base import BaseNameMatcher, CompanyUnderline


class OpenCalaisNameMatcher(BaseNameMatcher):
    """Match company names to underlines via OpenCalais
    """
    def __init__(self, access_token=None, *args, **kwargs):
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

    def _match_raw_names(self, names, retry=5, *args, **kwargs):
        if isinstance(names, str):
            names = [names]
        names = list(set(names))
        end, curr, step = len(names), 0, 50
        ret = {}
        while curr < end:
            range_end = curr + step if curr + step < end else end
            curr_names = names[curr:range_end]
            match_res = self._match_for_names(curr_names, retry=retry)
            if match_res:
                ret.update(match_res)
            curr = range_end
        return ret

    def _match_for_names(self, curr_names, retry=5):
        content = ''.join(
            ('{} is a public company\r\n').format(name) for name in curr_names
        ).encode('utf-8')
        link = 'https://api.thomsonreuters.com/permid/calais'
        for retry_num in range(retry):
            try:
                res = requests.post(
                    link, data=content, headers=self._get_headers(), timeout=80
                )
                res_content = res.content
                break
            except Exception as err:
                _get_internal_logger().error(
                    'Exception during requesting opencalais: %s', str(err)
                )
                if retry_num == retry - 1:
                    raise
        match, parent_match = self._process_rdf_response(res_content)
        ret_data = {}
        for name in curr_names:
            if name in self._cache:
                ret_data[name] = self._cache[name]
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
            if len(subjs) == 0:
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
        for name in match_top:
            raw_match_rec = match_top[name]
            orig_name, legal_name, ric, ticker, permid, score = raw_match_rec
            underline = CompanyUnderline(
                ticker=ticker, ric=ric, permid=permid
            )
            self._cache[orig_name] = (
                legal_name, underline, {'score': score, 'top': True}
            )
        for name in match:
            raw_match_rec = match[name]
            orig_name, legal_name, ric, ticker, permid, score = raw_match_rec
            underline = CompanyUnderline(
                ticker=ticker, ric=ric, permid=permid
            )
            self._cache[orig_name] = (
                legal_name, underline, {'score': score}
            )
        return match, match_top
