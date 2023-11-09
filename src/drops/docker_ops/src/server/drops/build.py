import os
import argparse
import sys

DESC = '''build the command under cmd to... /replase.'''
CMD_PATH = '../cmd'


def system(command):
    # os.system 在不同平台的行为不同，特别在 linux 下，是一个 16 位数，如果直接返回给 shell，会被截取低 8 位。这里做平台兼容。
    return os.system(command) % 256


def main():
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument('-d', '--dest',
                        help="Place the output into <path>.", type=str, default='../replase/')
    arg = parser.parse_args()
    for d in os.listdir(CMD_PATH):
        print('build', d)
        build_bin = 'go build -o ' + \
            os.path.join(arg.dest, '') + ' ' + os.path.join(CMD_PATH, d)
        s = system(build_bin)
        if s:
            sys.exit(s)


if __name__ == '__main__':
    main()
