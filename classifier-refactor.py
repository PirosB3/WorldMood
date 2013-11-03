import csv
import functools
import logging
import random

import nltk
import redis
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import stopwords

import formatting, phrase

N_INFORMATIVE_FEATURES= 2500
N_BIGRAMS= 100
N_CUTOFF = 1.0/3.0

logging.basicConfig(level=logging.INFO, format='[%(asctime)-15s %(module)s] %(message)s')
LOGGER = logging.getLogger(__name__) 

FORMATTER = formatting.FormatterPipeline(
    formatting.make_lowercase,
    formatting.strip_urls,
    formatting.strip_http,
    formatting.strip_hashtags,
    formatting.strip_names,
    formatting.replace_html_entities,
    formatting.remove_repetitons,
    functools.partial(
        formatting.remove_noise,
        stopwords = stopwords.words('english') + ['rt']
    ),
    #functools.partial(
        #formatting.stem_words,
        #stemmer= nltk.stem.porter.PorterStemmer()
    #)
    functools.partial(
        formatting.lemmatize_words,
        lemmatizer= nltk.stem.wordnet.WordNetLemmatizer()
    )
)

def get_csv(f):
    reader = csv.reader(f, delimiter=' ', quotechar='|')

    res = {
        'positive': [],
        'negative': []
    }

    for row in reader:
        res[row[1]] = row[0]

    return res['positive'], res['negative']

def get_phrases_from_redis_and_csv():
    make_phrase = functools.partial(phrase.Phrase, tokenizer=nltk.word_tokenize)

    client = redis.Redis()
    pos_redis = [make_phrase(p) for p in client.smembers('sentiment-analysis-3:positive')]
    neg_redis = [make_phrase(p) for p in client.smembers('sentiment-analysis-3:negative')]

    with open('handwriten_validated_output.csv', 'rb') as f:
        pos_csv, neg_csv = get_csv(f)
    pos_csv = map(make_phrase, pos_csv)
    neg_csv = map(make_phrase, neg_csv)

    return {
        'positive': pos_redis + pos_csv,
        'negative': neg_redis + neg_csv
    }

def get_phrases_from_redis():
    make_phrase = functools.partial(phrase.Phrase, tokenizer=nltk.word_tokenize)

    client = redis.Redis()
    pos_sentences = [make_phrase(p) for p in client.smembers('sentiment-analysis-3:positive')]
    neg_sentences = [make_phrase(p) for p in client.smembers('sentiment-analysis-3:negative')]

    return {
        'positive': pos_sentences,
        'negative': neg_sentences
    }


def build_features(phrases, split, n_informative_features=None, bigram_analyzer=None):
    res = []
    for sentiment_name, sentiment_phrases in phrases.iteritems():
        for p in sentiment_phrases:
            features = p.get_features(FORMATTER, n_informative_features, bigram_analyzer)
            if len(features.keys()) > 0:
                res.append((features, sentiment_name))

    random.shuffle(res)
    threshold = int(len(res) * split)
    LOGGER.info("Using %s for testing and %s for training" % (threshold, len(res) - threshold))
    return res[:threshold], res[threshold:]

def get_test_set(f, n_informative_features=None, bigram_analyzer=None):
    reader = csv.reader(f, delimiter=' ', quotechar='|')

    res = []
    for row in reader:
        p = phrase.Phrase(row[0], nltk.word_tokenize)
        features = p.get_features(FORMATTER, n_informative_features, bigram_analyzer)
        if len(features.keys()) > 0:
            print (features, row[1])
            res.append((features, row[1]))

    return res

def main():
    LOGGER.info("Started classifier")

    # Get training data from Redis
    #phrases = get_phrases_from_redis()
    phrases = get_phrases_from_redis_and_csv()

    # Initialize the Text Processor, get bigrams and informative features
    LOGGER.info("Building text processor")
    processor = phrase.TextProcessor(phrases, FORMATTER)

    LOGGER.info("Getting %s informative features" % N_INFORMATIVE_FEATURES)
    n_informative_features = processor.get_most_informative_features(N_INFORMATIVE_FEATURES)

    LOGGER.info("Getting %s best bigrams" % N_BIGRAMS)
    bigram_analyzer = processor.get_bigram_analyzer(N_BIGRAMS)

    LOGGER.info("Starting test iteration for 5 times.")

    # Test score against validation set
    test_set, train_set = build_features(phrases, N_CUTOFF, n_informative_features, bigram_analyzer)
    classifier = NaiveBayesClassifier.train(train_set)

    # Run iteration to see what combination gives best score
    best_score = 0
    for _ in range(5):
        # Get features
        test_set, train_set = build_features(phrases, N_CUTOFF, n_informative_features, bigram_analyzer)

        # Train classifier
        classifier = NaiveBayesClassifier.train(train_set)
        classifier.show_most_informative_features(10)
        score = nltk.classify.util.accuracy(classifier, test_set)

        best_score = max(best_score, score)
        LOGGER.info("Score is: %s" % score)



if __name__ == '__main__':
    main()
