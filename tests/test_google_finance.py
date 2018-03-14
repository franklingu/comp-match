from unittest import TestCase
from unittest.mock import patch, MagicMock

from matchers.google_finance import GoogleFinanceNameMatcher
from .helpers import MockedResponse


class GoogleFinanceTestCase(TestCase):
    @patch('matchers.google_finance.requests.session')
    def test_gf_success_matching(self, ses_mock):
        ses_mock.return_value = MagicMock(
            get=MagicMock(return_value=MockedResponse('gf_apple.html'))
        )
        gf_matcher = GoogleFinanceNameMatcher()
        symbols = gf_matcher.match_by('Apple Inc.')
        self.assertTrue('Apple Inc.' in symbols)
        self.assertTrue(len(symbols['Apple Inc.']) == 1)
        self.assertTrue(symbols['Apple Inc.'][0][0] == 'Apple Inc.')
        self.assertTrue(symbols['Apple Inc.'][0][1].ticker == 'AAPL')
        self.assertTrue(symbols['Apple Inc.'][0][1].country == 'US')
