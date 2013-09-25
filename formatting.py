import functools
import re

HASHTAG_RE = re.compile('#\w*[a-zA-Z_]+\w*')
NAME_RE = re.compile('@[A-Za-z0-9]+')
START_WITH_SPACE_RE = re.compile('^\s+')
END_WITH_SPACE_RE = re.compile('\s+$')

HTML_ENTITIES = {
  '&': '&amp;',
  '>': '&gt;',
  '<': '&lt;',
  '"': '&quot;',
  "'": '&#39;'
};

def _finalize_stripping(text):
    stripped_text= text
    for _re in [START_WITH_SPACE_RE, END_WITH_SPACE_RE]:
        stripped_text = _re.sub('', stripped_text)
    return stripped_text.replace('  ', ' ')

def _strip_re(context_re, text):
    stripped_text= context_re.sub('', text)
    return _finalize_stripping(stripped_text)

strip_hashtags = functools.partial(_strip_re, HASHTAG_RE)
strip_names = functools.partial(_strip_re, NAME_RE)

def replace_html_entities(text):
    stripped_text= text
    for to_replace, to_match in HTML_ENTITIES.iteritems():
        stripped_text = stripped_text.replace(to_match, to_replace)
    return _finalize_stripping(stripped_text)
