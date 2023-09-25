from . import globa

OFF = 0
FATAL = 1
ERROR = 2
WARN = 3
INFO = 4
DEBUG = 5
TRACE = 6
ALL = 7

LEVEL = INFO


def debug(*s):
    if globa.args.debug:
        print('debug:', *s)


def fatal(*s):
    if LEVEL >= FATAL:
        print('fatal:', *s)


def error(*s):
    if LEVEL >= ERROR:
        print('error:', *s)


def warn(*s):
    if LEVEL >= WARN:
        print('warn:', *s)


def info(*s):
    if LEVEL >= INFO:
        print('info:', *s)


def debug(*s):
    if LEVEL >= DEBUG:
        print('debug:', *s)


def trace(*s):
    if LEVEL >= TRACE:
        print('trace:', *s)


def run(*s):
    if LEVEL >= INFO:
        info('run >', *s)
