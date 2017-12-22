_RED = "\033[31m"
_RESET = "\033[0m"
_BOLDWHITE = "\033[1m\033[37m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_PURPLE = "\033[35m"
_CLEAR = "\033[2J"  # clears the terminal screen


def red(s):
    return _RED + s + _RESET


def cyan(s):
    return _CYAN + s + _RESET


def yellow(s):
    return _YELLOW + s + _RESET


def purple(s):
    return _PURPLE + s + _RESET


def white(s):
    return _BOLDWHITE + s + _RESET
