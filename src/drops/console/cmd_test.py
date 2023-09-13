from typing import Any
import unittest

from pkg import cmd
import tempfile
import os

class ObjectDict():
    def __init__(self, **args):
        self._data = args
    def __getattr__(self, name) -> Any:
        return self._data[name]
    def __setattr__(self, __name: str, __value: Any) -> None:
        self._data[__name] = __value

class virtualObj(dict):
    def __init__(self, *args, **kwargs):
        super(ObjectDict, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
        value =  self[name]
        if isinstance(value, dict):
            value = ObjectDict(value)
        return value

def args_enumerate():
    # 枚举全局测试参数
    argli = {
        'env':['dev', 'local'],
        'host':['example.drops.icu', ''],
        'port':[22, 22],
        'username': ['root', ''],
        'identity_file': ['~/.ssh/id_ed25519', ''],
        'password': ['1', ''],
        'encoding': ['utf-8', ''],
        'deploy_path': ['/srv/drops', '.'],
        'config': ['drops.yaml', ''],
    }
    data = {virtualObj(), virtualObj()}
    for k, i in argli.items():
        data[0][k]=i[0]
        data[1][k]=i[1]

    return data

def set_args_iter():
    # 迭代参数，设置全局变量
    for a in args_enumerate():
        cmd.globa.args = a
        yield(a)

class TestRemoteEnv(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._temp_dir = tempfile.TemporaryDirectory()
    def setUp(self):
        os.chdir(self._temp_dir.name)
    def tearDown(self):
        self._temp_dir.cleanup()
    def test_new(self):
        for _ in set_args_iter():
            self.setUp()
            cmd.new_cmd(virtualObj(dir_name='te', project_name='a'))
            self.tearDown()

if __name__ == '__main__':
    unittest.main()