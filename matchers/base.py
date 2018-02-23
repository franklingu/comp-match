"""Base classes for matchers
"""
from ._utils import (
    find_google_exchange, find_yahoo_exchange, find_country_for_exchange,
    find_country_repr,
)


class BaseNameMatcher(object):
    """Base for name matcher"""
    def __init__(self, *args, **kwargs):
        super(BaseNameMatcher, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def match_by(self, names):
        """Match by name

        Params:
            names: a company name or a list of company names

        Returns:
            dict of  orig_name: (mapped legal name, underline, addon info dict)
        """
        raise NotImplementedError('To be completed ...')


class CompanyUnderline(object):
    """Representation of a company underline"""
    def __init__(self, *args, **kwargs):
        super(CompanyUnderline, self).__init__()
        strict_validate = False
        if 'strict_validate' in kwargs:
            strict_validate = kwargs.pop('strict_validate')
        if 'ticker' in kwargs:
            self.ticker = kwargs.pop('ticker')
        if 'exchange' in kwargs:
            self.exchange = kwargs.pop('exchange')
        if 'google_exch' in kwargs:
            self.google_exch = kwargs.pop('google_exch')
        if 'yahoo_exch' in kwargs:
            self.yahoo_exch = kwargs.pop('yahoo_exch')
        if 'country' in kwargs:
            self.country = kwargs.pop('country')
        self.setup_exchange()
        self.setup_country()
        self.validate(strict_validate)

    @property
    def exch(self):
        return getattr(self, 'exchange', None)

    def setup_exchange(self):
        """Set exchange based on known information
        """
        if hasattr(self, 'exchange') and self.exchange is not None:
            return
        if hasattr(self, 'google_exch'):
            self.exchange = find_google_exchange(self.google_exch)
            return
        if hasattr(self, 'yahoo_exch'):
            self.exchange = find_yahoo_exchange(self.yahoo_exch)
            return

    def setup_country(self):
        """Set country based on known information
        """
        if not hasattr(self, 'exchange') or self.exchange is None:
            return
        exch_country = find_country_for_exchange(self.exchange)
        if hasattr(self, 'country') and self.country:
            if self.country == exch_country:
                return
        self.country = exch_country

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
            getattr(self, 'ticker', 'None'), getattr(self, 'exchange', 'None'),
            find_country_repr(getattr(self, 'country', 'UN'))
        )

    def __str__(self):
        return repr(self)

    def __hash__(self):
        return hash(repr(self))
