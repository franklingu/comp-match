"""Helper for test
"""
import os


class MockedResponse(object):
    def __init__(self, res_path):
        act_path = os.path.normpath(
            os.path.join(os.path.realpath(__file__), '../resources/', res_path)
        )
        self.act_path = act_path

    @property
    def status_code(self):
        return 200

    @property
    def content(self):
        with open(self.act_path, 'rb') as ifile:
            return ifile.read()
