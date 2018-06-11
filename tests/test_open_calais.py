"""Unit test for open_calais
"""
from unittest.mock import patch, MagicMock

from comp_match.open_calais import OpenCalaisNameMatcher
from .helpers import MockedResponse


@patch('requests.post', return_value=MockedResponse('oc_apple.rdf'))
@patch('requests.Session')
def test_oc_success_matching(session_mock, post_mock):
    """Test open calais success at first try
    """
    act_session = MagicMock()
    session_mock.return_value.__enter__.return_value = act_session
    act_session.get.return_value = MockedResponse('oc_apple.json')
    oc_matcher = OpenCalaisNameMatcher()
    symbols = oc_matcher.match_by('Apple', sleep=0)
    assert 'Apple' in symbols
    assert symbols['Apple'][0][0] == 'APPLE INC.'
    assert symbols['Apple'][0][1].ticker == 'AAPL'
    assert symbols['Apple'][0][1].country_code == 'US'
    # get html page first in session
    assert act_session.get.call_count == 2
    assert post_mock.call_count == 1


@patch('requests.post', return_value=MockedResponse('oc_apple.rdf', fails=2))
@patch('requests.Session')
def test_oc_retry_matching(session_mock, post_mock):
    """Test open calais success after retry
    """
    act_session = MagicMock()
    session_mock.return_value.__enter__.return_value = act_session
    act_session.get.return_value = MockedResponse('oc_apple.json', fails=3)
    oc_matcher = OpenCalaisNameMatcher()
    symbols = oc_matcher.match_by('Apple', sleep=0)
    assert 'Apple' in symbols
    assert symbols['Apple'][0][0] == 'APPLE INC.'
    assert symbols['Apple'][0][1].ticker == 'AAPL'
    assert symbols['Apple'][0][1].country_code == 'US'
    assert act_session.get.call_count == 5
    assert post_mock.call_count == 3


@patch('requests.post', return_value=MockedResponse('oc_google.rdf'))
@patch('requests.Session')
def test_oc_success_matching_with_top(session_mock, post_mock):
    """Test open calais success at first try
    """
    act_session = MagicMock()
    session_mock.return_value.__enter__.return_value = act_session
    act_session.get.return_value = MockedResponse('oc_google.json')
    oc_matcher = OpenCalaisNameMatcher()
    symbols = oc_matcher.match_by('Google', sleep=0)
    assert 'Google' in symbols
    assert symbols['Google'][0][0] == 'ALPHABET INC.'
    assert symbols['Google'][0][1].ticker == 'GOOGL'
    assert symbols['Google'][0][1].country_code == 'US'
    # get html page first in session
    assert act_session.get.call_count == 2
    assert post_mock.call_count == 1
