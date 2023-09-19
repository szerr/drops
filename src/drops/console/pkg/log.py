from . import globa


def debug(*s):
    if globa.args.debug:
        print('debug:', *s)


def warning(*s):
    print('Warning:', *s)


def info(*s):
    print('Info:', *s)


def run(*s):
    info('run >', *s)
