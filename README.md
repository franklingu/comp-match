# comp-match

[![Build Status](https://travis-ci.org/franklingu/comp-match.svg?branch=master)](https://travis-ci.org/franklingu/comp-match)&nbsp;
[![Documentation Status](https://readthedocs.org/projects/comp-match/badge/?version=latest)](http://comp-match.readthedocs.io/en/latest/?badge=latest)

*Match company names to legal names and underlines with a snap of finger*

## Contents

* [Intro](#intro)
* [Quick Start](#quick-start)
* [Documentation](#documentation)
* [Roadmap](#roadmap)
* [Contribution Guide](#contribution-guide)
* [Changelog](#changelog)
* [Notes](#notes)
* [License](#license)

## Intro

Given a company name, how to find its underline/stock symbol? By hand this does not seem like a very difficult task, but what if we need to match a lof of them? In such case we need to find a simple and effective way to compare company names, match to stock symbols.

## Quick Start

Install the package with ```pip install comp-match``` and check the installation is successful by ```python -c 'import comp_match; print(comp_match.__version__)'```. After successful installation, you should be able to see version printed out.

The following code snippet is a demo:

```
import comp_match

comp_match.match(['Apple', 'Google', 'Facebook', 'CitiBank'])
"""
Returned response, takes some time
{'Apple': [['Apple Inc.',
   CompanyUnderline: [AAPL@NASDAQ OMX PHLX@US],
   {'exch': 'NAS',
    'exch_desc': 'NASDAQ',
    'ric': 'AAPL.OQ',
    'score': 4.9837301}],
  ['Apple Hospitality REIT Inc',
   CompanyUnderline: [APLE@New York Stock Exchange@US],
   {'exch': 'NYQ', 'exch_desc': 'NYSE', 'score': 2.0}],
  ['Apple Inc.',
   CompanyUnderline: [APC@XETRA@DE],
   {'exch': 'FRA', 'exch_desc': 'Frankfurt', 'score': 2.0}],
  ...
  ['Apple Inc.',
   CompanyUnderline: [AAPL@Vienna Stock Exchange@AT],
   {'exch': 'VIE', 'exch_desc': 'Vienna', 'score': 1.0}],
  ['Apple',
   CompanyUnderline: [AAPL.EUR@@UN],
   {'exch': 'EBS', 'exch_desc': 'Swiss', 'score': 1.0}]],
 'CitiBank': [['CITIGROUP INC.',
   CompanyUnderline: [C@New York Stock Exchange@US],
   {'ric': 'C.N', 'score': 3.0}]],
 'Facebook': [['Facebook, Inc. Common Stock',
   CompanyUnderline: [FB@NASDAQ OMX PHLX@US],
   {'exch': 'NAS', 'exch_desc': 'NASDAQ', 'ric': 'FB.OQ', 'score': 4.9795589}],
  ['Facebook, Inc. Common Stock',
   CompanyUnderline: [FB2A@XETRA@DE],
   {'exch': 'GER', 'exch_desc': 'XETRA', 'score': 4.0}],
  ...
  ['Facebook',
   CompanyUnderline: [FB.USD@@UN],
   {'exch': 'EBS', 'exch_desc': 'Swiss', 'score': 1.0}]],
 'Google': [['GOOGLE LLC', None, {'ric': '', 'score': 3.0}],
  ['CBOE Equity VIX ON Google', CompanyUnderline: [VXGOG@@UN], {'score': 1.0}],
  ['CBOE Equity VIX ON Google', CompanyUnderline: [VXIBM@@UN], {'score': 1.0}],
  ['Alphabet Inc.',
   CompanyUnderline: [GOOG@@US],
   {'exch': 'NGM', 'exch_desc': 'NASDAQ', 'score': 1.0}],
  ['Alphabet Inc.',
   CompanyUnderline: [GOOGL@@US],
   {'exch': 'NAS', 'exch_desc': 'NASDAQ', 'score': 1.0}],
  ...
  ['Alphabet Inc.',
   CompanyUnderline: [GOOGL@Mexico Stock Exchange@MX],
   {'exch': 'MEX', 'exch_desc': 'Mexico', 'score': 1.0}]]}

"""
```

## Documentation

TODO

## Roadmap

- [x] Get GoogleFinance, YahooFinance, OpenCalais matchers working
- [x] Add top level function to match company names to underlines directly
- [ ] Add more documentation
- [ ] Double check GoogleFinance and YahooFinance exchange mapping
- [ ] Improve performance with asyncio or threading
- [ ] Add msn finance matching
- [ ] Improve result matching and filtering with similary check, weight adjustment
- [ ] Add command line usage
- [ ] Add in memory caching
- [ ] Add redis / db caching
- [ ] Add Flask web app and json api

## Contribution Guide

TODO

## Changelog

[Changelog](./changelog)

## Notes

1. Information is gathered from web and inaccuracy is inevitable. In particularly Google Finance and Yahoo Finance exchange mapping relies on some third party website and therefore may not be 100% correct. I am still trying to verify those information.
2. Tickers do change and currently there is not support for mapping over history yet.

### License

[MIT](./LICENSE)
