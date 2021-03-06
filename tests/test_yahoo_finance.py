"""Test YahooFinanceNameMatcher
"""
from unittest.mock import patch

from comp_match.yahoo_finance import YahooFinanceNameMatcher
from .helpers import MockedResponse


@patch('requests.get', return_value=MockedResponse('yh_apple.json'))
def test_yh_success_matching(get_mock):
    """Test YahooFinance match successfully
    """
    yh_matcher = YahooFinanceNameMatcher()
    symbols = yh_matcher.match_by('Apple')
    try:
        get_mock.assert_called_once()
    except AttributeError:
        assert get_mock.call_count == 1
    assert 'Apple' in symbols
    assert symbols['Apple'][0][1].ticker == 'AAPL'
    assert symbols['Apple'][0][1].country_code == 'US'
    assert symbols['Apple'][2][1].country_code == 'MX'

@patch('requests.get', return_value=MockedResponse('yh_apple.json', fails=2))
def test_yh_matching_with_exception(get_mock):
    """Test YahooFinance match with network exception
    """
    yh_matcher = YahooFinanceNameMatcher()
    symbols = yh_matcher.match_by('Apple', sleep=0)
    assert get_mock.call_count == 3
    assert 'Apple' in symbols
    assert symbols['Apple'][0][1].ticker == 'AAPL'
    assert symbols['Apple'][0][1].country_code == 'US'
    symbols = yh_matcher.match_by('Apple', retry=2, sleep=0)
    try:
        get_mock.assert_called()
    except AttributeError:
        assert get_mock.called
    assert not symbols['Apple']

@patch('requests.get', return_value=MockedResponse('yh_zhihu.json'))
def test_yh_multiple_matching(get_mock):
    """Test YahooFinance match to multiple results
    """
    yh_matcher = YahooFinanceNameMatcher()
    symbols = yh_matcher.match_by('zhihu')
    try:
        get_mock.assert_called_once()
    except AttributeError:
        assert get_mock.call_count == 1
    assert 'zhihu' in symbols
    assert symbols['zhihu'][0][1].ticker == '603156'
    assert symbols['zhihu'][0][1].country_code == 'CN'
