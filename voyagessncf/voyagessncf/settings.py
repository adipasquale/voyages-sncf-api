import os


BOT_NAME = 'voyagessncf'

SPIDER_MODULES = ['voyagessncf.spiders']
NEWSPIDER_MODULE = 'voyagessncf.spiders'

ITEM_PIPELINES = {}
current_dir = os.path.dirname(os.path.realpath(__file__))

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36'
DEFAULT_REQUEST_HEADERS = {
  'Accept-Encoding': 'gzip, deflate',
  'Accept-Language': 'fr',
}

MONGO_URI = "localhost:27017"
MONGO_DATABASE = "offers"
