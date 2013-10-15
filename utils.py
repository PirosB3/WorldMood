
def batch_get_features(phrases, n_features=None, bigram_analyzer=None):
    res = {}
    for classification, phrases in phrases.iteritems():
        res[classification] = [p.get_features(n_features, bigram_analyzer)
                                for p in phrases]
    return res
