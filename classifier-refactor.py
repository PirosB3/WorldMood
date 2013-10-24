import functools
import random

import nltk
import redis
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import stopwords

import formatting, phrase

FORMATTER = formatting.FormatterPipeline(
    formatting.make_lowercase,
    formatting.strip_urls,
    formatting.strip_hashtags,
    formatting.strip_names,
    formatting.replace_html_entities,
    formatting.remove_repetitons,
    functools.partial(
        formatting.remove_noise,
        stopwords = stopwords.words('english') + ['rt']
    ),
    functools.partial(
        formatting.stem_words,
        stemmer= nltk.stem.porter.PorterStemmer()
    ),
    functools.partial(
        formatting.lemmatize_words,
        lemmatizer= nltk.stem.wordnet.WordNetLemmatizer()
    )
)

def get_phrases_from_redis():
    make_phrase = functools.partial(phrase.Phrase, tokenizer=nltk.word_tokenize)

    client = redis.Redis()
    pos_sentences = [make_phrase(p) for p in client.smembers('sentiment-analysis-3:positive')]
    neg_sentences = [make_phrase(p) for p in client.smembers('sentiment-analysis-3:negative')]
    neutral_sentences = [make_phrase(p) for p in client.smembers('sentiment-analysis-4:neutral')]
    return {
        'positive': pos_sentences,
        'negative': neg_sentences
        #'neutral': neutral_sentences
    }


def build_features(phrases, split, n_informative_features, bigram_analyzer):
    res = []
    for sentiment_name, sentiment_phrases in phrases.iteritems():
        for p in sentiment_phrases:
            features = p.get_features(FORMATTER, n_informative_features, bigram_analyzer)
            res.append((features, sentiment_name))

    random.shuffle(res)
    threshold = int(len(res) * split)
    return res[:threshold], res[threshold:]

def main():
    # Get training data from Redis
    phrases = get_phrases_from_redis()

    # Initialize the Text Processor, get bigrams and informative features
    processor = phrase.TextProcessor(phrases, FORMATTER)
    n_informative_features = processor.get_most_informative_features(1150)
    bigram_analyzer = processor.get_bigram_analyzer(100)

    # Get features
    train_set, test_set = build_features(phrases, 1.0/4.0, n_informative_features, bigram_analyzer)

    # Train classifier
    classifier = NaiveBayesClassifier.train(train_set)
    classifier.show_most_informative_features(10)
    print nltk.classify.util.accuracy(classifier, test_set)


if __name__ == '__main__':
    main()
