from typing import Any
import unittest

import pkg
import tempfile
import os, random

work_path = '.'

def randstr(i):
    s = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.sample(s, i))

class virtualObj(dict):
    def __init__(self, *args, **kwargs):
        super(virtualObj, self).__init__(*args, **kwargs)
 
    def __getattr__(self, name):
        return self[name]

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

class TestRemoteEnv(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
    def setUp(self):
        os.chdir(work_path.name)
        self.args = gen_messy_args()
        pkg.globa.args = self.args
    def tearDown(self):
        work_path.cleanup()
    def test_new(self):
        pkg.cmd.new_cmd(virtualObj(project_name='te'))
        project_path = os.path.join(work_path.name, 'te')
        with open(os.path.join(project_path, self.args.config)) as fd:
            conf = fd.read()
        check_messy_conf(self.assertTrue, self.args, conf)

if __name__ == '__main__':
    work_path = tempfile.TemporaryDirectory()
    unittest.main()