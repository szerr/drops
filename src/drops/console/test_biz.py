import os.path
import unittest
import tempfile
from test_lib import gen_messy_args, check_messy_conf, randstr
import pkg
from pkg import biz


class TestNew(unittest.TestCase):
    def setUp(self):
        self.testTempDir = tempfile.TemporaryDirectory()
        self.projectName = 'te' + randstr(3)
        self.args = gen_messy_args()
        pkg.globa.args = self.args
        self.cmd_list = []
        biz.system.system = lambda i: self.cmd_list.append(i)
        self.env = pkg.config.gen_env_by_args(self.args)

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


if __name__ == '__main__':
    unittest.main()
