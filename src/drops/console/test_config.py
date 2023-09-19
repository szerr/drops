import unittest

import pkg
import tempfile, os

from test_lib import gen_messy_args, check_messy_env, check_env, randstr

class TestConfig(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
    def setUp(self):
        self.args = gen_messy_args()
        pkg.globa.args = self.args
        env = pkg.config.gen_env_by_args(self.args)
        self.env = env
        self.work_path = tempfile.TemporaryDirectory()
        os.chdir(self.work_path.name)
    def tearDown(self):
        self.work_path.cleanup()
    def test_env(self):
        check_messy_env(self.assertEqual, self.args, self.env)
    def test_config(self):
        # 测试新建和保存
        self.project_name = randstr(4)
        pkg.config.Conf().init_template(self.project_name).set_env(self.env).save()
        conf = pkg.config.Conf().open()
        check_env(self.assertEqual, conf.get_env(self.env.env), self.env)
        self.assertEqual(conf.project_name(), self.project_name)
        # 测试更改
        conf.remove_env(self.env.env)
        self.args = gen_messy_args()
        self.env = pkg.config.gen_env_by_args(self.args)
        conf.set_env(self.env)
        self.project_name = randstr(6)
        conf.set_project_name(self.project_name)
        conf.save()
        conf = pkg.config.Conf().open()
        check_env(self.assertEqual, conf.get_env(self.env.env), self.env)
        self.assertEqual(conf.project_name(), self.project_name)

if __name__ == '__main__':
    unittest.main()