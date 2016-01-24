from scrapy.exceptions import DropItem
import pymongo


class DuplicatesPipeline(object):

  def __init__(self):
      self.hashes = set()

  def process_item(self, item, spider):
    item_hash = hash(tuple(sorted(item.items())))
    if item_hash in self.hashes:
      raise DropItem("Duplicate item found: %s" % item)
    else:
      self.hashes.add(item_hash)
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
