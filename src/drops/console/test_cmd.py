from typing import Any
import unittest

import pkg
import tempfile
import os
from test_lib import gen_messy_args,  check_messy_conf, virtualObj, randstr


class TestRemoteEnv(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def setUp(self):
        self.project_name = randstr(4)
        self.work_path = tempfile.TemporaryDirectory()
        os.chdir(self.work_path.name)
        self.args = gen_messy_args(self.project_name)
        pkg.globa.args = self.args

    def tearDown(self):
        self.work_path.cleanup()

    def test_new(self):
        pkg.cmd.new_cmd(virtualObj(project_path='te'))
        project_path = os.path.join(self.work_path.name, 'te')
        with open(os.path.join(project_path, self.args.config)) as fd:
            conf = fd.read()
        check_messy_conf(self.assertTrue, self.args, conf)


if __name__ == '__main__':
    unittest.main()
