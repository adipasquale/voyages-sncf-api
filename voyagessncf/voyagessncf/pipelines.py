from scrapy.exceptions import DropItem


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
