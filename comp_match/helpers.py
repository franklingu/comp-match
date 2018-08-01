"""Helper functions to company names more easily
"""
from .base import BaseNameMatcher
from .exceptions import UnkownMatcherException


MATCHERS_MAP = dict(
    (cls.AGENT, cls) for cls in BaseNameMatcher.__subclasses__()
)
MATCHERS_WEIGHT = dict((matcher_name, 1) for matcher_name in MATCHERS_MAP)
# Give Open Calais more weight in matching
MATCHERS_WEIGHT['open_calais'] += 2


def match(company_names, matchers=None, matchers_configs=None):
    """Match company names to company underlines

    Args:
        company_names: company name or list of company names to match underlines for
        matchers: list of matcher classes to use
        matchers_configs: matcher class custom config
    """
    def merge_match_results(match_results):
        """Merge match results and compute weight
        """
        merged = {}
        for company_name, matches in match_results.items():
            match_map = {}
            for match_record, weight in matches:
                legal_name, underline, extra = match_record
                score = weight * float(extra.get('score', 1))
                if underline not in match_map:
                    extra['score'] = score
                    match_map[underline] = [legal_name, underline, extra]
                else:
                    legal_name, underline, bextra = match_map[underline]
                    extra.update(bextra)
                    extra['score'] += score
                    match_map[underline][2] = extra
            merged[company_name] = sorted(
                list(match_map.values()), key=lambda x: -x[2]['score']
            )
        return merged

    if isinstance(company_names, str):
        company_names = [company_names]
    if matchers_configs is None:
        matchers_configs = {}
    if matchers is None:
        matchers = list(MATCHERS_MAP.keys())
    match_results = {}
    for matcher_name in matchers:
        try:
            if matcher_name not in matchers_configs:
                matcher = MATCHERS_MAP[matcher_name]()
            else:
                config_args, config_kwargs = matchers_configs[matcher_name]
                matcher = MATCHERS_MAP[matcher_name](
                    *config_args, **config_kwargs
                )
            result = matcher.match_by(company_names)
            for name, elems in result.items():
                if name not in match_results:
                    match_results[name] = []
                for elem in elems:
                    match_results[name].append(
                        (elem, MATCHERS_WEIGHT.get(matcher_name, 0))
                    )
        except KeyError:
            raise UnkownMatcherException(
                '{} is unkown as a matcher'.format(matcher_name)
            )
        except ValueError:
            raise
    return merge_match_results(match_results)
