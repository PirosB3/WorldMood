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
        text = "Keep calm &amp; carry on"
        result = formatting.replace_html_entities(text)
        self.assertEqual(result, "Keep calm & carry on")

    def test_should_remove_stopwords(self):
        text = "it's the best"
        result = formatting.remove_noise(text, ['it', 'the'])
        self.assertEqual(result, "best")

    def test_should_remove_repetitive_chars(self):
        text = "Helloooooo world I ammm comingggg"
        result = formatting.remove_repetitons(text)
        self.assertEqual(result, "Hello world I am coming")

    def test_workflow(self):
        wf = formatting.FormatterPipeline(
            formatting.strip_hashtags,
            formatting.strip_names
        )
        result = wf.process('#fucking @aaaaa #asjdhga Hello world #lorem 123 #1psum')
        self.assertEqual(result, 'Hello world 123')
