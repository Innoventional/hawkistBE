import re

__author__ = 'ne_luboff'


def get_users_from_comment(text):
    """
    Parse comment text and get all people from it.
    """
    text = text.decode('utf-8')
    matches = re.findall(r'\B@([\w\d.-]+)($|\s|[^\w\d@])', text, re.U)
    return [tag[0] for tag in matches]

if __name__ == '__main__':
    print get_users_from_comment("a @f jkjks @fdfdf @_k.o.a-q_")
