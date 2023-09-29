from . import globa

OFF = 0
FATAL = 1
ERROR = 2
WARN = 3
INFO = 4
DEBUG = 5
TRACE = 6
ALL = 7

_LEVEL_STR = {"off": OFF,
              "fatal": FATAL,
              "error": ERROR,
              "warn": WARN,
              "info": INFO,
              "debug": DEBUG,
              "trace": TRACE,
              "all": ALL}

_LEVEL = INFO


def set_level_str(s):
    set_level(_LEVEL_STR['s'])


def set_level(level):
    _LEVEL = level


def debug(*s):
    if globa.args.debug:
        print('debug:', *s)


def fatal(*s):
    if _LEVEL >= FATAL:
        print('fatal:', *s)


def error(*s):
    if _LEVEL >= ERROR:
        print('error:', *s)


def warn(*s):
    if _LEVEL >= WARN:
        print('warn:', *s)


def info(*s):
    if _LEVEL >= INFO:
        print('info:', *s)


def debug(*s):
    if _LEVEL >= DEBUG:
        print('debug:', *s)


def trace(*s):
    if _LEVEL >= TRACE:
        print('trace:', *s)


def run(*s):
    if _LEVEL >= INFO:
        info('run >', *s)
