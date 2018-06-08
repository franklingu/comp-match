"""Base classes for matchers
"""
from abc import ABCMeta
import random

from ._utils import resource_manager


class BaseNameMatcher(  # pylint: disable=too-few-public-methods
        object, metaclass=ABCMeta):
    """Base for name matcher"""
    def __init__(self, *args, **kwargs):
        """

        TODO: add cache
        """
        super(BaseNameMatcher, self).__init__()
        self.args = args
        self.kwargs = kwargs
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


    def match_by(self, names, **kwargs):
        """Match by names

        Params:
            names: a company name or a list of company names

        Returns:
            dict of  orig_name: list of \
            mapped legal name, underline, addon info dict)
        """
        if isinstance(names, str):
            names = [names]
        names = set(names)
        return self._match_by(names, **kwargs)

    def _match_by(self, names, **kwargs):
        raise NotImplementedError('To be implemented')


class CompanyUnderline(object):
    """Representation of a company underline"""
    def __init__(self, **kwargs):
        super(CompanyUnderline, self).__init__()
        strict_validate = False
        if 'strict_validate' in kwargs:
            strict_validate = kwargs.pop('strict_validate')
        if kwargs.get('ticker'):
            self.ticker = kwargs.pop('ticker')
        if kwargs.get('exchange'):
            self.exchange = kwargs.pop('exchange')
        if kwargs.get('mic'):
            self.mic = kwargs.pop('mic')
        if kwargs.get('google_exch'):
            self.google_exch = kwargs.pop('google_exch')
        if kwargs.get('yahoo_exch'):
            self.yahoo_exch = kwargs.pop('yahoo_exch')
        if kwargs.get('country_code'):
            self.country_code = kwargs.pop('country_code')
        self.setup_exchange()
        self.validate(strict_validate)

    @property
    def exch(self):
        return getattr(self, 'exchange', None)

    def setup_exchange(self):
        """Set exchange based on known information
        """
        def set_exchange(self, attr):
            if hasattr(self, attr):
                cond = {attr: getattr(self, attr, '')}
                match = resource_manager.find_exchange_by(**cond)
                if match is not None:
                    self.exchange = match['Exchange Name']
                    if match['Country Code']:
                        self.country_code = match['Country Code']

        if hasattr(self, 'exchange') and self.exchange is not None:
            return
        for attr in ['google_exch', 'yahoo_exch', 'mic']:
            set_exchange(self, attr)

    def validate(self, strict_validate=False):
        """Validate the current presentation of an underline

        Params:
            strict_validate: if true, both exchange and ticker should be set;
                if false, only ticker is required
        Raises:
            ValueError
        """
        if not hasattr(self, 'ticker') or self.ticker is None:
            raise ValueError('Ticker is required')
        if not strict_validate:
            return
        if not hasattr(self, 'exchange') or self.exchange is None:
            raise ValueError('Exchange is required')

    def __repr__(self):
        return 'CompanyUnderline: [{}@{}@{}]'.format(
            getattr(self, 'ticker', ''),
            getattr(self, 'exchange', ''),
            getattr(self, 'country_code', 'UN')
        )

    def __str__(self):
        return '{}@{}'.format(
            getattr(self, 'ticker', ''),
            getattr(self, 'country_code', 'UN')
        )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))
