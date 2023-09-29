import os.path
import unittest
import tempfile
from test_lib import gen_messy_args, check_messy_conf, randstr
import pkg
from pkg import biz


class TestNew(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.project_name = 'te' + randstr(3)
        self.args = gen_messy_args()
        pkg.globa.args = self.args
        self.env = pkg.config.gen_env_by_args(self.args)
        # 替换依赖项目

    def tearDown(self):
        self.test_dir.cleanup()

    def test_new(self):
        pkg.biz.new_project(self.project_name, self.test_dir.name)
        project_path = os.path.join(self.test_dir.name, self.project_name)
        self.assertTrue(os.path.isdir(project_path))
        conf_path = os.path.join(project_path, self.args.config)
        self.assertTrue(os.path.isfile(conf_path))
        with open(conf_path) as fd:
            check_messy_conf(self.assertTrue, self.args, fd.read())

    def test_init(self):
        pkg.biz.init_project(self.project_name, self.test_dir.name)
        self.assertTrue(os.path.isdir(self.test_dir.name))
        conf_path = os.path.join(self.test_dir.name, self.args.config)
        self.assertTrue(os.path.isfile(conf_path))
        with open(conf_path) as fd:
            check_messy_conf(self.assertTrue, self.args, fd.read())


class TestRsync(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        os.chdir(self.test_dir.name)
        self.project_name = 'te' + randstr(3)
        self.args = gen_messy_args()
        pkg.globa.args = self.args
        self.env = pkg.config.gen_env_by_args(self.args)
        self.cmd_list = []
        # 替换依赖项目
        biz.system.system = lambda i: self.cmd_list.append(i)

    def tearDown(self):
        self.test_dir.cleanup()

    def rsync2remotely(self, src, target):
        cmd = 'rsync -avzP --del -e "ssh -p ' + str(self.env.port)\
            + ' -i ' + self.env.identity_file \
            + '"  --exclude ./.gitignore --exclude ./.git --exclude ./' + self.args.config \
            + ' --exclude ./src --exclude ./secret '+src+' ' + self.env.username \
            + '@' + self.env.host + ':' + target
        self.assertEqual(self.cmd_list[0], cmd)

    def rsync2local(self, src, target):
        cmd = 'rsync -avzP --del -e "ssh -p ' + str(self.env.port)\
            + ' -i ' + self.env.identity_file \
            + '" ' + self.env.username \
            + '@' + self.env.host + ':'+src+' ' + target
        self.assertEqual(self.cmd_list[0], cmd)

    def rsync2local_link_dest(self, src, target, link_dest):
        cmd = 'rsync -avzP --del -e "ssh -p ' + str(self.env.port)\
            + ' -i ' + self.env.identity_file \
            + '" --link-dest='+link_dest+' ' + self.env.username \
            + '@' + self.env.host + ':'+src+' ' + target
        self.assertEqual(self.cmd_list[0], cmd)

    def test_rsync_release(self):
        biz.rsync_release(self.env)
        self.rsync2remotely('release', self.env.get_deploy_path())

    def test_rsync_docker(self):
        os.getcwd()
        biz.rsync_docker(self.env)
        print(self.cmd_list)


if __name__ == '__main__':
    biz.log._LEVEL = biz.log.OFF
    unittest.main()
