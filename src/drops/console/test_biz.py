import os.path
import unittest
import tempfile
from test_lib import gen_messy_args, check_messy_conf, randstr
import pkg
from pkg import biz
import time


class TestNew(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        os.chdir(self.test_dir.name)
        self.project_name = 'te' + randstr(3)
        self.args = gen_messy_args(self.project_name)
        pkg.globa.args = self.args
        self.env = pkg.config.gen_env_by_args(self.project_name, self.args)
        # 替换依赖项目

    def tearDown(self):
        self.test_dir.cleanup()

    def test_new(self):
        pkg.biz.new_project(os.path.join(
            self.test_dir.name, self.project_name))
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
        self.args = gen_messy_args(self.project_name)
        pkg.globa.args = self.args
        self.env = pkg.config.gen_env_by_args(self.project_name, self.args)
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


class TestBackup(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        os.chdir(self.test_dir.name)
        self.project_name = 'te' + randstr(3)
        self.args = gen_messy_args(self.project_name)
        pkg.globa.args = self.args
        self.env = pkg.config.gen_env_by_args(self.project_name, self.args)
        pkg.config.Conf().init_template(self.project_name).set_env(
            self.env).save(pkg.globa.args.config)
        self.cmd_list = []
        # 替换依赖项目
        biz.rsync_backup = lambda *i: self.cmd_list.append(i)

    def tearDown(self):
        self.test_dir.cleanup()

    def verify_call(self, link_desc='', *items, keep_backups=-1, bak_tag=''):
        self.assertEqual(len(items), len(self.cmd_list))
        for k in items:
            source_path = '/srv/drops/%s/%s' % (self.project_name, k)
            if not k.endswith('yaml'):
                source_path += '/'  # '/' 结尾代表文件夹
            target_path = 'backup/%s/' % (k)
            for i in self.cmd_list:
                if source_path == i[1]:
                    break
            else:
                self.assertEqual(source_path, ','.join(
                    [i[1] for i in self.cmd_list]))
            for i in self.cmd_list:
                if target_path in i[2]:
                    break
            else:
                self.assertEqual(target_path, ','.join(
                    [i[2] for i in self.cmd_list]))
            # 测试 link
            if link_desc:
                if i in self.cmd_list:
                    link = os.path.join(self.test_dir.name,
                                        'backup', k, link_desc)
                    self.assertEqual(link, i[3])
            # 测试保留备份
            if keep_backups > 0:
                exist_li = os.listdir(target_path)
                self.assertEqual(len(exist_li), keep_backups)
                for i in list(range(10))[0-keep_backups:]:
                    self.assertTrue(bak_tag+str(i) in exist_li)

    def test_backup_all(self):
        backup_path = 'backup'
        biz.backup(self.env, 'all', backup_path)
        self.verify_call('', 'release', 'servers', 'var',
                         'volumes', 'docker-compose.yaml')

        # 顺便做 --link-dest 和 保留备份 的测试
        bak_tag = randstr(4)
        # 模拟备份副本的年份，用199开头避免冲突。加上0-9，用 '%Y' 识别成年份。
        bak_tag_time = bak_tag + '199'
        for t in range(10):
            tag = bak_tag_time + str(t)
            for i in ('release', 'servers', 'var', 'volumes'):
                os.makedirs(os.path.join(backup_path, i, tag))
            with open(os.path.join(os.path.join(backup_path, 'docker-compose.yaml'), tag), 'w') as fd:
                pass
        self.cmd_list = []
        biz.backup(self.env, 'all', 'backup', bak_tag+'%Y', keep_backups=3)
        self.verify_call(tag, 'release', 'servers', 'var',
                         'volumes', 'docker-compose.yaml', keep_backups=3, bak_tag=bak_tag_time)

    def test_backup_ops(self):
        biz.backup(self.env, 'ops', 'backup')
        self.verify_call('', 'release', 'servers', 'docker-compose.yaml')

    def test_backup_docker(self):
        biz.backup(self.env, 'docker', 'backup')
        self.verify_call('', 'docker-compose.yaml')

    def test_backup_release(self):
        biz.backup(self.env, 'release', 'backup')
        self.verify_call('', 'release')

    def test_backup_servers(self):
        biz.backup(self.env, 'servers', 'backup')
        self.verify_call('', 'servers')

    def test_backup_var(self):
        biz.backup(self.env, 'var', 'backup')
        self.verify_call('', 'var')

    def test_backup_volumes(self):
        biz.backup(self.env, 'volumes', 'backup')
        self.verify_call('', 'volumes')


if __name__ == '__main__':
    biz.log._LEVEL = biz.log.OFF
    unittest.main()
