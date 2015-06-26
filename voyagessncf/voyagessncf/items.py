import scrapy


class Offer(scrapy.Item):
  direction = scrapy.Field()
  price = scrapy.Field()
  departure_time = scrapy.Field()
  departure_station = scrapy.Field()
  arrival_time = scrapy.Field()
  arrival_station = scrapy.Field()
  duration = scrapy.Field()
  changes = scrapy.Field()
