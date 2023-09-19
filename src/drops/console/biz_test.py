import os.path
import unittest
import tempfile, random

def randstr(i):
    s = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.sample(s, i))

class virtualObj():
    def __init__(self, **kwargs):
        self._data = kwargs
    def __getattr__(self, item):
        return self._data[item]

def gen_messy_args():
    # 随意的填一填命令行参数
    args = virtualObj(
        env='production'+randstr(3),
        host='example.drops.icu'+randstr(3),
        port=random.randint(0, 30000),
        username='root'+randstr(3),
        identity_file='~/.ssh/id_ed25519'+randstr(3),
        password=randstr(3),
        encoding='utf-8'+randstr(3),
        deploy_path='/srv/drops/te'+randstr(3),
        config='drops.yaml'+randstr(3),
        env_type='remote',
    )
    return args

def check_messy_conf(assertTrue, args, conf):
    assertTrue('  '+args.env+':' in conf)
    assertTrue('    host: '+args.host in conf)
    assertTrue('    port: '+str(args.port) in conf)
    assertTrue('    username: '+args.username in conf)
    assertTrue('    identity_file: '+args.identity_file in conf)
    assertTrue('    password: '+args.password in conf)
    assertTrue('    encoding: '+args.encoding in conf)
    assertTrue('    deploy_path: '+args.deploy_path in conf)
    assertTrue('    type: '+args.env_type in conf)

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
    import pkg  # 为了单个文件调试
    unittest.main()
else:
    from . import pkg  # 同时又能作为包被引入
