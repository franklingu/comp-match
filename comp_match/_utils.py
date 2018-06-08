"""Collection of util functions
"""
import os
import csv
import logging
try:
    import simplejson as json
except ImportError:
    import json


__all__ = [
    'get_logger', 'resource_manager',
]


class ResourceManager(object):
    def __init__(self, exchange_path=None, country_path=None, mic_path=None):
        super(ResourceManager, self).__init__()
        dirpath = os.path.dirname(os.path.abspath(__file__))
        if exchange_path is None:
            exchange_path = os.path.normpath(os.path.join(
                dirpath, './resources/exchanges.csv'
            ))
        if country_path is None:
            country_path = os.path.normpath(os.path.join(
                dirpath, './resources/iso_countries.json'
            ))
        if mic_path is None:
            mic_path = os.path.normpath(os.path.join(
                dirpath, './resources/iso_10383.csv'
            ))
        with open(exchange_path, 'r') as ifile:
            reader = csv.reader(ifile, delimiter='|')
            exchanges, google_exches, yahoo_exches, mics = {}, {}, {}, {}
            headers = None
            for row in reader:
                if headers is None:
                    headers = row
                    continue
                rec = dict(zip(headers, row))
                exchanges[rec['Exchange Name']] = rec
                if rec.get('Google Exchange'):
                    google_exches[rec['Google Exchange']] = rec
                if rec.get('Yahoo Exchange'):
                    yahoo_exches[rec['Yahoo Exchange']] = rec
                if rec.get('MIC'):
                    mics[rec['MIC']] = rec
            self.exchanges = exchanges
            self.google_exches = google_exches
            self.yahoo_exches = yahoo_exches
            self.mics = mics
        with open(mic_path, 'r', encoding='latin1') as ifile:
            reader = csv.reader(ifile, delimiter=',')
            mheaders = None
            for row in reader:
                if mheaders is None:
                    mheaders = row
                    continue
                mrec = dict(zip(mheaders, row))
                rec = dict((h, '') for h in headers)
                rec['Country Name'] = mrec['COUNTRY']
                rec['Country Code'] = mrec['ISO COUNTRY CODE (ISO 3166)']
                rec['MIC'] = mrec['MIC']
                rec['Operating MIC'] = mrec['OPERATING MIC']
                rec['Exchange Name'] = mrec['NAME-INSTITUTION DESCRIPTION']
                if rec['MIC'] not in self.mics:
                    self.mics[rec['MIC']] = rec
        with open(country_path, 'r') as ifile:
            raw_countries = json.load(ifile)['3166-1']
            countries = {}
            for country in raw_countries:
                countries[country['name']] = country
            self.countries = countries

    def find_exchange_by(self, **kwargs):
        """match to raw exchange dict by given criteria
        """
        if 'exchange' in kwargs:
            return self.exchanges.get(kwargs['exchange'])
        elif 'google_exch' in kwargs:
            return self.google_exches.get(kwargs['google_exch'])
        elif 'yahoo_exch' in kwargs:
            return self.yahoo_exches.get(kwargs['yahoo_exch'])
        elif 'mic' in kwargs:
            return self.mics.get(kwargs['mic'])
        else:
            raise ValueError('Unknown exchange type for matching')

    def find_country_by(self, **kwargs):
        """match to raw country dict by given criteria
        """
        if kwargs['country'] in self.countries:
            return self.countries[kwargs['country']]
        return None


resource_manager = ResourceManager()


def get_logger():
    """Return internal logger
    """
    return logging.getLogger('comp_match')
