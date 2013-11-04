import collections
import csv
import functools
import logging
import random

import nltk
import redis
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import stopwords
from nltk.tokenize import WhitespaceTokenizer

from scipy.optimize import anneal

import formatting, phrase

N_DATASET_ITERATIONS= 5
N_INFORMATIVE_FEATURES= 4000
N_BIGRAMS= 2000
N_CUTOFF = 1.0/4.0

logging.basicConfig(level=logging.INFO, format='[%(asctime)-15s %(module)s] %(message)s')
LOGGER = logging.getLogger(__name__) 

TOKENIZER = WhitespaceTokenizer().tokenize
FORMATTER = formatting.FormatterPipeline(
    formatting.make_lowercase,
    formatting.strip_urls,
    formatting.strip_hashtags,
    formatting.strip_names,
    formatting.remove_repetitons,
    formatting.replace_html_entities,
    formatting.strip_nonchars,
    functools.partial(
        formatting.remove_noise,
        stopwords = stopwords.words('english') + ['rt']
    ),
    #functools.partial(
        #formatting.stem_words,
        #stemmer= nltk.stem.porter.PorterStemmer()
    #)
    #functools.partial(
        #formatting.lemmatize_words,
        #lemmatizer= nltk.stem.wordnet.WordNetLemmatizer()
    #)
)

def get_csv(f):
    res = collections.defaultdict(list)

    reader = csv.reader(f, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for row in reader:
        res[row[1]].append(row[0])

    return res['positive'], res['negative']

def get_phrases_from_redis_and_csv():
    make_phrase = functools.partial(phrase.Phrase, tokenizer=TOKENIZER)

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

def convert_phrases_to_feature_vectors(data, n_informative_features, bigram_analyzer):
    res = []
    for p, sentiment in data:
        features = p.get_features(FORMATTER, n_informative_features, bigram_analyzer)
        if len(features.keys()) > 0:
            res.append((features, sentiment))
        else:
            #LOGGER.info("Dropped phrase: %s. %s" % (p.get_text(), p.get_features(FORMATTER)))
            print "%s. %s" % (p.get_text(), p.get_formatted_text(FORMATTER))
    return res

def split_phrase_data(phrases, split):
    res = []
    for sentiment_name, sentiment_phrases in phrases.iteritems():
        for p in sentiment_phrases:
            res.append((p, sentiment_name))

    random.shuffle(res)
    threshold = int(len(res) * split)
    LOGGER.info("Using %s for testing and %s for training" % (threshold, len(res) - threshold))
    return res[:threshold], res[threshold:]

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

def main():
    LOGGER.info("Started classifier")

    # Get training data from Redis and CSV
    phrases = get_phrases_from_redis_and_csv()

    # Initialize the Text Processor, get bigrams and informative features
    LOGGER.info("Building text processor")
    processor = phrase.TextProcessor(phrases, FORMATTER)
    LOGGER.info("Getting %s informative features" % N_INFORMATIVE_FEATURES)
    n_informative_features = processor.get_most_informative_features(N_INFORMATIVE_FEATURES)
    LOGGER.info("Getting %s best bigrams" % N_BIGRAMS)
    bigram_analyzer = processor.get_bigram_analyzer(N_BIGRAMS)

    # Run iteration to see what combination gives best score
    LOGGER.info("Starting test iteration for 5 times.")
    best_score = 0
    best_data_set = None
    for _ in range(N_DATASET_ITERATIONS):

        # Get training and testing set and convert to features with default parameters
        test_set, train_set = split_phrase_data(phrases, N_CUTOFF)
        test_set_features = convert_phrases_to_feature_vectors(test_set, n_informative_features, bigram_analyzer)
        train_set_features = convert_phrases_to_feature_vectors(train_set, n_informative_features, bigram_analyzer)

        # Train classifier
        classifier = NaiveBayesClassifier.train(train_set_features)
        score = nltk.classify.util.accuracy(classifier, test_set_features)

        LOGGER.info("Score for iteration #%s is: %s" % (_ + 1, score))
        best_score = max(best_score, score)
        if best_score == score:
            best_data_set = test_set, train_set

    # Best iteration has been done, now let's tune the params
    LOGGER.info("BEST ITERATION IS: %s" % best_score)


if __name__ == '__main__':
    main()
