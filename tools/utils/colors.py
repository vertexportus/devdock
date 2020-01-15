color_dict = {
    'RED': '1;31',
    'GREEN': '1;32',
    'YELLOW': '1;33',
    'BLUE': '1;36'
}


def red(text):
    return f"\x1b[{color_dict['RED']}m{text}\x1b[0m"


def green(text):
    return f"\x1b[{color_dict['GREEN']}m{text}\x1b[0m"


def yellow(text):
    return f"\x1b[{color_dict['YELLOW']}m{text}\x1b[0m"


def blue(text):
    return f"\x1b[{color_dict['BLUE']}m{text}\x1b[0m"
