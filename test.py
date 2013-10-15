import unittest
import mock

import formatting
import phrase

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

class PhraseTestCase(unittest.TestCase):

    def setUp(self):
        self.formatter = mock.Mock()

    def test_should_accept_a_formatter(self):
        self.formatter.process.return_value = ['hello', 'world']
        w = phrase.Phrase("Hello World", self.formatter)

        self.assertEqual(w.get_text(), "Hello World")
        self.assertEqual(w.get_formatted_text(), ['hello', 'world'])

    def test_should_build_feature_dict(self):
        self.formatter.process.return_value = ['hello', 'world']
        w = phrase.Phrase("Hello World", self.formatter)

        self.assertEqual(w.get_features(), {
            'has(hello)': True,
            'has(world)': True
        })

    def test_should_build_feature_dict_with_exclusion_list(self):
        self.formatter.process.return_value = ['hello', 'world']
        w = phrase.Phrase("Hello World", self.formatter)

        n_informative_features = ['hello']
        self.assertEqual(w.get_features(include_only=n_informative_features), {
            'has(hello)': True
        })

    def test_should_build_feature_dict_with_bigrams(self):
        self.formatter.process.return_value = ['i', 'have', 'machine', 'gun']
        w = phrase.Phrase("I have a machine gun", self.formatter)

        ba = mock.Mock()
        ba.scan_features_for_bigrams.return_value = [('machine', 'gun')]
        self.assertEqual(w.get_features(bigram_analyzer=ba), {
            'has(i)': True,
            'has(have)': True,
            'has(machine)': True,
            'has(gun)': True,
            'has(machine,gun)': True,
        })


class BigramAnalyzerTestCase(unittest.TestCase):

    def setUp(self):
        self.bigrams = [
            ('machine', 'gun'),
            ('machine', 'man'),
            ('hello', 'world'),
        ]

    def test_formatter(self):
        b = phrase.BigramAnalyzer(self.bigrams)
        self.assertEqual(2, len(b.formatted_bigrams['machine']))
        self.assertEqual(1, len(b.formatted_bigrams['hello']))

    def test_can_find(self):
        b = phrase.BigramAnalyzer(self.bigrams)

        res = b.find_bigrams_for('machine')
        self.assertEqual(res, ['gun', 'man'])

        res = b.find_bigrams_for('hello')
        self.assertEqual(res, ['world'])

    def test_can_scan(self):
        b = phrase.BigramAnalyzer(self.bigrams)

        features = ['hello', 'machine', 'gun', 'world']
        res = b.scan_features_for_bigrams(features)
        self.assertEqual([('machine', 'gun')], res)

        features = ['hello', 'hello', 'world']
        res = b.scan_features_for_bigrams(features)
        self.assertEqual([('hello', 'world')], res)


class TextProcessorTestCase(unittest.TestCase):

    def setUp(self):
        self.freq_dist = mock.MagicMock()
        self.cond_freq_dist = mock.MagicMock()

        p1 = mock.Mock()
        p1.get_formatted_text.return_value = ['lorem', 'ipsum']

        p2 = mock.Mock()
        p2.get_formatted_text.return_value = ['i', 'feel', 'so', 'lorem', 'cool', 'today']

        self.data = {
            'pos': [p1],
            'neg': [p2]
        }

    def test_should_convert_to_words(self):
        tp = phrase.TextProcessor(self.data)
        fd, cfd = tp._build_prob_dist(self.freq_dist, self.cond_freq_dist)
        self.assertEqual(8, fd.inc.call_count)
