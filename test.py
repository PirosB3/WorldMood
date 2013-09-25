import unittest

import formatting

class FormattingTestCase(unittest.TestCase):

    def test_should_strip_hashtags(self):
        text = '#fucking #asjdhga Hello world #lorem 123 #1psum'
        result = formatting.strip_hashtags(text)
        self.assertEqual(result, 'Hello world 123')

    def test_should_strip_names(self):
        text = "Hey @lorem, hows it goin? I'm with @1psum"
        result = formatting.strip_names(text)
        self.assertEqual(result, "Hey , hows it goin? I'm with")

    def test_should_replace_html_entities(self):
