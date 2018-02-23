import pytest

from matchers.base import BaseNameMatcher


def test_matcher_base_class():
    with pytest.raises(NotImplementedError):
        base = BaseNameMatcher()
        base.match_by('')
