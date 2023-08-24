import os, argparse

DESC = '''build the command under cmd to... /replase.'''
CMD_PATH = '../cmd'

def main():
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument('-o','--out-path',
                    help="Place the output into <path>.", type=str, default='../replase')
    arg = parser.parse_args()
    for d in os.listdir(CMD_PATH):
        print('go build', d)
        os.system('go build -o '+os.path.join(arg.out_path, '') + ' ' + os.path.join(CMD_PATH, d))

if __name__ == '__main__':
    main()
