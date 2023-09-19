import os.path
import unittest
import tempfile
from test_lib import gen_messy_args, check_messy_conf, randstr
import pkg 

class TestNew(unittest.TestCase):
    def setUp(self):
        self.testTempDir = tempfile.TemporaryDirectory()
        self.projectName = 'te' + randstr(3)
        self.args = gen_messy_args()
        pkg.globa.args = self.args

    def tearDown(self):
        self.testTempDir.cleanup()

    def test_new(self):
        pkg.biz.new_project(self.projectName, self.testTempDir.name)
        project_path = os.path.join(self.testTempDir.name, self.projectName)
        self.assertTrue(os.path.isdir(project_path))
        conf_path = os.path.join(project_path, self.args.config)
        self.assertTrue(os.path.isfile(conf_path))
        with open(conf_path) as fd:
            check_messy_conf(self.assertTrue, self.args, fd.read())

    def test_init(self):
        pkg.biz.init_project(self.projectName, self.testTempDir.name)
        self.assertTrue(os.path.isdir(self.testTempDir.name))
        conf_path = os.path.join(self.testTempDir.name, self.args.config)
        self.assertTrue(os.path.isfile(conf_path))
        with open(conf_path) as fd:
            check_messy_conf(self.assertTrue, self.args, fd.read())

if __name__ == '__main__':
    unittest.main()
