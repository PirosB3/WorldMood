from nltk.probability import ELEProbDist


def cached(function):
    cache = {}
    def wrapper(*args):
        try:
            return cache[args[1:]]
        except KeyError:
            result = function(*args)
            cache[args[1:]] = result 
            return result
    return wrapper


class RedisConditionalFreqDist(object):

    def __init__(self, db, feature_key, label):
        self._db = db
        self._feature_key = feature_key
        self._label = label

    def _get_class_existence(self, label):
        return self._db.hexists(self._feature_key, label)

    def _get_class_weight(self, label):
        res = self._db.hget(self._feature_key, label)
        if not res:
            return 0
        return res

    def keys(self):
        if self._get_class_existence(self._label):
            return [True, None]
        return [None]

    def __getitem__(self, key):
        if key == True:
            try:
                return self._db.hget(self._feature_key, self._label)
            except TypeError:
                return 0
        if key == None:
            classes = self._db.hgetall(self._feature_key)
            return classes['total'] - classes[self._label]

        raise Exception("Class works only with None and True")

    #def values(self):
        #return self._db.hvals(self._hash_key)

    #def N(self):
        #return int(self._db.get(self._n_key))

    #def B(self):
        #return int(self._db.get(self._b_key))

    #def __contains__(self, key):
        #return self._db.hexists(self._hash_key, key)


class RedisLabelFeatureDist(object):
    def __init__(self, db, partial_key):
        self._db = db
        self._partial_key = partial_key
        self._fds = {}

    def __contains__(self, args):
        klass, feat = args
        return feat in self.get_fd(klass)

    def get_fd(self, label):
        try:
            return self._fds[label]
        except KeyError:
            self._fds[label] = self._make_fd(label)
        return self._fds[label]

    def _make_fd(self, label):
        key = ':'.join([self._partial_key, label])
        return ELEProbDist(RedisFreqDist(self._db, key))


class RedisFreqDist(dict):
    def __init__(self, db, hash_key):
        self._db = db
        self._hash_key = hash_key
        self._n_key = ':'.join([self._hash_key, 'count'])
        self._b_key = ':'.join([self._hash_key, 'keycount'])

    def keys(self):
        return self._db.hkeys(self._hash_key)

    def __getitem__(self, key):
        return int(self._db.hget(self._hash_key, key))

    def values(self):
        return self._db.hvals(self._hash_key)

    def N(self):
        return int(self._db.get(self._n_key))

    def B(self):
        return int(self._db.get(self._b_key))

    def __contains__(self, key):
        return self._db.hexists(self._hash_key, key)


class RedisDataSource(object):
    def __init__(self, db, root_key, classes_keys):
        self.db = db
        self.root_key = root_key
        self.classes_keys = classes_keys

    def get_classes(self):
        return self.classes_keys

    def get_data(self, constructor=None):
        res = {}
        for cls in self.classes_keys:
            data = self.db.smembers('%s:%s' % (self.root_key, cls))
            if constructor:
                data = map(constructor, data)
            res[cls] = data
        return res
