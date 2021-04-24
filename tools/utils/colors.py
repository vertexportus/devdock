color_dict = {
    'RED': '0;31',
    'GREEN': '0;32',
    'YELLOW': '0;33',
    'BYELLOW': '1;33',
    'BLUE': '0;36'
}


def red(text):
    return f"\x1b[{color_dict['RED']}m{text}\x1b[0m"


def green(text):
    return f"\x1b[{color_dict['GREEN']}m{text}\x1b[0m"


def yellow(text):
    return f"\x1b[{color_dict['YELLOW']}m{text}\x1b[0m"


def byellow(text):
    return f"\x1b[{color_dict['BYELLOW']}m{text}\x1b[0m"


def blue(text):
    return f"\x1b[{color_dict['BLUE']}m{text}\x1b[0m"
