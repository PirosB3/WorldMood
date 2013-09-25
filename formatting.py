import functools
import re

HASHTAG_RE = re.compile('#\w*[a-zA-Z_]+\w*')
NAME_RE = re.compile('@[A-Za-z0-9]+')
START_WITH_SPACE_RE = re.compile('^\s+')
END_WITH_SPACE_RE = re.compile('\s+$')

def _strip_re(context_re, text):
    stripped_text= text
    for _re in [context_re, START_WITH_SPACE_RE, END_WITH_SPACE_RE]:
        stripped_text = _re.sub('', stripped_text)
    return stripped_text.replace('  ', ' ')

strip_hashtags = functools.partial(_strip_re, HASHTAG_RE)
strip_names = functools.partial(_strip_re, NAME_RE)
