import gettext


def translate_str(message: str) -> str:
    return gettext.gettext(message)


def translate_str_gimp(message: str) -> str:
    return message
