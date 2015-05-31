import scrapy


class Offer(scrapy.Item):
  direction = scrapy.Field()
  price = scrapy.Field()
