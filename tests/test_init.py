"""Test init and helper in comp_match

Serve as a high-level integration test
"""
from comp_match import match


def test_match():
    """Test match function in comp_match.helpers
    """
    match_res = match(['Apple'])
    assert 'Apple' in match_res
    assert match_res['Apple'][0][0].title() == 'Apple Inc.'
    assert match_res['Apple'][0][1].ticker == 'AAPL'
    assert match_res['Apple'][0][1].country_code == 'US'
