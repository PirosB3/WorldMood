
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
