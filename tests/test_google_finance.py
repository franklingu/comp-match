from unittest.mock import patch

from comp_match.google_finance import GoogleFinanceNameMatcher
from .helpers import MockedResponse


@patch('requests.get', return_value=MockedResponse('gf_apple.html'))
def test_gf_success_matching(get_mock):
    gf_matcher = GoogleFinanceNameMatcher()
    symbols = gf_matcher.match_by('Apple Inc.')
    try:
        get_mock.assert_called_once()
    except AttributeError:
        assert get_mock.call_count == 1
    assert 'Apple Inc.' in symbols
    assert len(symbols['Apple Inc.']) == 1
    assert symbols['Apple Inc.'][0][0] == 'Apple Inc.'
    assert symbols['Apple Inc.'][0][1].ticker == 'AAPL'
    assert symbols['Apple Inc.'][0][1].country == 'US'

@patch('requests.get', return_value=MockedResponse('gf_apple.html', fails=2))
def test_gf_matching_with_exception(get_mock):
    gf_matcher = GoogleFinanceNameMatcher()
    symbols = gf_matcher.match_by('Apple Inc.', sleep=0)
    assert get_mock.call_count == 3
    assert symbols['Apple Inc.'][0][0] == 'Apple Inc.'
    assert symbols['Apple Inc.'][0][1].ticker == 'AAPL'
    assert symbols['Apple Inc.'][0][1].country == 'US'
    symbols = gf_matcher.match_by('Apple Inc.', retry=2, sleep=0)
    try:
        get_mock.assert_called()
    except AttributeError:
        assert get_mock.called
    assert not symbols['Apple Inc.']

@patch('requests.get', return_value=MockedResponse('gf_zhihu.html'))
def test_gf_multiple_matching(get_mock):
    gf_matcher = GoogleFinanceNameMatcher()
    symbols = gf_matcher.match_by('zhihu')
    try:
        get_mock.assert_called_once()
    except AttributeError:
        assert get_mock.call_count == 1
    assert 'zhihu' in symbols
    assert len(symbols['zhihu']) == 7
