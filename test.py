import unittest
import mock

import data_sources
import formatting
import phrase
import utils

from nltk import word_tokenize

class WordTestCase(unittest.TestCase):

    def test_should_accept_a_word_and_process_with_formatter(self):
        formatter = mock.Mock()
        formatter.process_word.return_value = None

        w = phrase.Word('hello')
        self.assertEqual('hello', w.get_word())
        self.assertFalse(w.get_formatted_word(formatter))

class FormattingTestCase(unittest.TestCase):

    def test_should_strip_hashtags(self):
        text = '#fucking'
        result = formatting.strip_hashtags(text)
        self.assertFalse(result)

    def test_should_remove_non_chars(self):
        text = '#12oclock'
        result = formatting.strip_nonchars(text)
        self.assertEqual(result, 'oclock')

    def test_should_strip_names(self):
        text = "@lorem"
        result = formatting.strip_names(text)
        self.assertFalse(result)

    def test_should_replace_html_entities(self):
        text = "&amp;"
        result = formatting.replace_html_entities(text)
        self.assertEqual(result, "&")

    def test_should_remove_stopwords(self):
        text = "it's"
        result = formatting.remove_noise(text, ['it', 'the'])
        self.assertFalse(result)

    def test_should_remove_repetitive_chars(self):
        text = "blooooooooooood"
        result = formatting.remove_repetitons(text)
        self.assertEqual(result, "blood")

        text = "hello"
        result = formatting.remove_repetitons(text)
        self.assertEqual(result, "hello")

        text = "weeeeeeeeeeee"
        result = formatting.remove_repetitons(text)
        self.assertEqual(result, "wee")

        text = "xxxxxxxxxxxyyxxxxxxxxxxxx"
        result = formatting.remove_repetitons(text)
        self.assertEqual(result, "xxyyxx")

class PhraseTestCase(unittest.TestCase):

    def setUp(self):
        self.formatter = mock.Mock()

    def test_should_get_text_and_formatted(self):

        def side_effect(word):
            if word == 'fucking':
                return None
            return word.lower()
        self.formatter.process_word.side_effect = side_effect

        w = phrase.Phrase("Hello fucking World", word_tokenize)
        self.assertEqual(w.get_text(), 'Hello fucking World')
        self.assertEqual(w.get_formatted_text(self.formatter), ['hello', 'world'])

    def test_should_build_feature_dict(self):

        def side_effect(word):
            return word.lower()

        self.formatter.process_word.side_effect = side_effect
        w = phrase.Phrase("Hello World", word_tokenize)

        self.assertEqual(w.get_features(self.formatter), {
            'has(hello)': True,
            'has(world)': True
        })

    def test_should_build_feature_dict_with_exclusion_list(self):

        def side_effect(word):
            return word.lower()

        self.formatter.process_word.side_effect = side_effect
        w = phrase.Phrase("Hello World", word_tokenize)

        n_informative_features = ['hello']
        result = w.get_features(self.formatter, n_features=n_informative_features)
        self.assertEqual(result, {'has(hello)': True})

    def test_should_build_feature_dict_with_bigrams(self):
        w = phrase.Phrase("I have a machine gun", word_tokenize)
        w.get_formatted_text = mock.Mock(return_value=['i', 'have', 'machine', 'gun'])

        ba = mock.Mock()
        ba.scan_features_for_bigrams.return_value = [('machine', 'gun')]
        self.assertEqual(w.get_features(self.formatter, bigram_analyzer=ba), {
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
        tp = phrase.TextProcessor(self.data, None)
        fd, cfd = tp._build_prob_dist(self.freq_dist, self.cond_freq_dist)
        self.assertEqual(8, fd.inc.call_count)

class UtilsTestCase(unittest.TestCase):

    def setUp(self):
        self.p = mock.Mock()
        self.p.get_features.return_value = {
            'has(i)': True,
            'has(have)': True,
            'has(machine)': True,
            'has(gun)': True,
            'has(machine,gun)': True,
        }

    def test_can_process_batch(self):
        res = utils.batch_get_features({
            'pos': [self.p, self.p, self.p],
            'neg': [self.p, self.p, self.p]
        })
        self.assertEqual(2, len(res.keys()))
        self.assertTrue(res['pos'][0]['has(i)'])

class RedisDataSourceTestCase(unittest.TestCase):

    def setUp(self):
        def _side_effect(key):
            if key == 'stanford-corpus:positive':
                return ['I am positive', 'me too!']
            if key == 'stanford-corpus:negative':
                return ['I am negative']

        self.db = mock.MagicMock()
        self.db.smembers.side_effect = _side_effect

    def test_it_initializes(self):
        ds = data_sources.RedisDataSource(self.db, 'stanford-corpus', ['positive', 'negative'])
        self.assertEqual(len(ds.get_classes()), 2)

    def test_get_data(self):
        ds = data_sources.RedisDataSource(self.db, 'stanford-corpus', ['positive', 'negative'])

        sentiments = ds.get_data()
        self.assertEqual(len(sentiments.keys()), 2)
        self.assertEqual(sentiments['positive'][0], 'I am positive')
        self.assertEqual(sentiments['negative'][0], 'I am negative')

    def test_get_data_constructor(self):
        ds = data_sources.RedisDataSource(self.db, 'stanford-corpus', ['positive', 'negative'])
        c = mock.MagicMock()

        sentiments = ds.get_data(c)
        self.assertEqual(c.call_count, 3)
