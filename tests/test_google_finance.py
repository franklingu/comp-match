from unittest.mock import patch

from comp_match.google_finance import GoogleFinanceNameMatcher
from .helpers import MockedResponse


@patch('requests.get', return_value=MockedResponse('gf_apple.json'))
def test_gf_success_matching(get_mock):
    gf_matcher = GoogleFinanceNameMatcher()
    symbols = gf_matcher.match_by('apple')
    try:
        get_mock.assert_called_once()
    except AttributeError:
        assert get_mock.call_count == 1
    assert 'apple' in symbols
    assert len(symbols['apple']) == 6
    assert symbols['apple'][0][0] == 'Apple Inc.'
    assert symbols['apple'][0][1].ticker == 'AAPL'
    assert symbols['apple'][0][1].country_code == 'US'

@patch('requests.get', return_value=MockedResponse('gf_apple.json', fails=2))
def test_gf_matching_with_exception(get_mock):
    gf_matcher = GoogleFinanceNameMatcher()
    symbols = gf_matcher.match_by('apple', sleep=0)
    assert get_mock.call_count == 3
    assert symbols['apple'][0][0] == 'Apple Inc.'
    assert symbols['apple'][0][1].ticker == 'AAPL'
    assert symbols['apple'][0][1].country_code == 'US'
    symbols = gf_matcher.match_by('apple', retry=2, sleep=0)
    try:
        get_mock.assert_called()
    except AttributeError:
        assert get_mock.called
    assert not symbols['apple']

@patch('requests.get', return_value=MockedResponse('gf_zhihu.json'))
def test_gf_multiple_matching(get_mock):
    gf_matcher = GoogleFinanceNameMatcher()
    symbols = gf_matcher.match_by('zhihu')
    try:
        get_mock.assert_called_once()
    except AttributeError:
        assert get_mock.call_count == 1
    assert 'zhihu' in symbols
    assert len(symbols['zhihu']) == 3
