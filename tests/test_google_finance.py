from unittest.mock import patch

from matchers.google_finance import GoogleFinanceNameMatcher
from .helpers import MockedResponse


@patch('requests.get', return_value=MockedResponse('gf_apple.html'))
def test_gf_success_matching(get_mock):
    gf_matcher = GoogleFinanceNameMatcher()
    symbols = gf_matcher.match_by('Apple Inc.')
    get_mock.assert_called_once()
    assert 'Apple Inc.' in symbols
    assert len(symbols['Apple Inc.']) == 1
    assert symbols['Apple Inc.'][0][0] == 'Apple Inc.'
    assert symbols['Apple Inc.'][0][1].ticker == 'AAPL'
    assert symbols['Apple Inc.'][0][1].country == 'US'

@patch('requests.get', return_value=MockedResponse('gf_apple.html', fails=2))
def test_gf_matching_with_exception(get_mock):
    gf_matcher = GoogleFinanceNameMatcher()
    symbols = gf_matcher.match_by('Apple Inc.', sleep=0)
    get_mock.assert_called()
    assert symbols['Apple Inc.'][0][0] == 'Apple Inc.'
    assert symbols['Apple Inc.'][0][1].ticker == 'AAPL'
    assert symbols['Apple Inc.'][0][1].country == 'US'
    symbols = gf_matcher.match_by('Apple Inc.', retry=2, sleep=0)
    get_mock.assert_called()
    assert not symbols['Apple Inc.']

@patch('requests.get', return_value=MockedResponse('gf_zhihu.html'))
def test_gf_multiple_matching(get_mock):
    gf_matcher = GoogleFinanceNameMatcher()
    symbols = gf_matcher.match_by('zhihu')
    get_mock.assert_called_once()
    assert 'zhihu' in symbols
    assert len(symbols['zhihu']) == 7
