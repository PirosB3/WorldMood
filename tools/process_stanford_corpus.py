import csv
import redis
import sys

SENTIMENT_MAP = {
    '0': 'negative',
    '2': 'neutral',
    '4': 'positive'
}

def main():
    with open(sys.argv[1]) as f:
        r = redis.Redis()
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            sentiment_name = SENTIMENT_MAP[row[0]]
            sentiment_text = row[5]
            print sentiment_text, sentiment_name
            r.sadd('stanford-corpus:%s' % sentiment_name, sentiment_text)


if __name__ == '__main__':
    main()
