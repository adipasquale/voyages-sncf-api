from scrapy.exceptions import DropItem
import pymongo


class DuplicatesPipeline(object):

  def __init__(self):
      self.all_items = set()

  def process_item(self, item, spider):
    if item in self.all_items:
      raise DropItem("Duplicate item found: %s" % item)
    else:
      self.ids_seen.add(item)
      return item


class MongoDBPipeline(object):

  collection_name = 'offers'

  def __init__(self, mongo_uri, mongo_db):
    self.mongo_uri = mongo_uri
    self.mongo_db = mongo_db

  @classmethod
  def from_crawler(cls, crawler):
    return cls(
      mongo_uri=crawler.settings.get('MONGO_URI'),
      mongo_db=crawler.settings.get('MONGO_DATABASE')
    )

  def open_spider(self, spider):
    self.client = pymongo.MongoClient(self.mongo_uri)
    self.db = self.client[self.mongo_db]

  def close_spider(self, spider):
    self.client.close()

  def process_item(self, item, spider):
    self.db[self.collection_name].insert(dict(item, **{"request_id": spider.request_id}))
    return item
