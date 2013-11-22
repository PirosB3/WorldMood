import functools

import nltk
from nltk.corpus import stopwords

import formatting

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
    functools.partial(
        formatting.stem_words,
        stemmer= nltk.stem.porter.PorterStemmer()
    )
    #functools.partial(
        #formatting.lemmatize_words,
        #lemmatizer= nltk.stem.wordnet.WordNetLemmatizer()
    #)
)
