import random


def randstr(i):
    s = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.sample(s, i))


class virtualObj(dict):
    def __init__(self, *args, **kwargs):
        super(virtualObj, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
        return self[name]


def gen_messy_args(project_name):
    # 随意的填一填命令行参数
    args = virtualObj(
        env='production'+randstr(3),
        host='example.drops.icu'+randstr(3),
        port=random.randint(0, 30000),
        username='root'+randstr(3),
        identity_file='~/.ssh/id_ed25519'+randstr(3),
        password=randstr(3),
        deploy_path='/srv/drops/' + project_name,
        encoding='utf-8'+randstr(3),
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


def check_messy_env(assertEqual, args, env):
    assertEqual(args.env, env.name)
    assertEqual(args.host, env.host)
    assertEqual(args.port, env.port)
    assertEqual(args.username, env.username)
    assertEqual(args.identity_file, env.identity_file)
    assertEqual(args.password, env.password)
    assertEqual(args.encoding, env.encoding)
    assertEqual(args.deploy_path, env.deploy_path)
    assertEqual(args.env_type, env.type)


def check_env(assertEqual, env1, env2):
    assertEqual(env1.name, env2.name)
    assertEqual(env1.host, env2.host)
    assertEqual(env1.port, env2.port)
    assertEqual(env1.username, env2.username)
    assertEqual(env1.identity_file, env2.identity_file)
    assertEqual(env1.password, env2.password)
    assertEqual(env1.encoding, env2.encoding)
    assertEqual(env1.deploy_path, env2.deploy_path)
    assertEqual(env1.type, env2.type)
