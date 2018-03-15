"""Helper for test
"""
import os


class MockedResponse(object):
    def __init__(self, res_paths, fails=0, raises=ValueError):
        if isinstance(res_paths, str):
            res_paths = [res_paths]
        act_paths = []
        for res_path in res_paths:
            act_path = os.path.normpath(os.path.join(
                os.path.realpath(__file__), '../resources/', res_path
            ))
            act_paths.append(act_path)
        self.act_paths = act_paths
        self.fails = fails
        self.num = 0
        self.raises = raises

    @property
    def status_code(self):
        return 200

    @property
    def content(self):
        self.num = self.num + 1
        idx = self.num // (self.fails + 1) - 1
        remainder = self.num % (self.fails + 1)
        if remainder == 0:
            act_path = self.act_paths[idx]
            with open(act_path, 'rb') as ifile:
                return ifile.read()
        else:
            raise self.raises('Mocked exception')
