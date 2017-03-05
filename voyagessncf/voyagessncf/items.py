import scrapy


class Offer(scrapy.Item):
  price = scrapy.Field()
  departure_time_readable = scrapy.Field()
  departure_datetime = scrapy.Field()
  departure_station = scrapy.Field()
  departure_station_code = scrapy.Field()
  arrival_datetime = scrapy.Field()
  arrival_time_readable = scrapy.Field()
  arrival_station = scrapy.Field()
  arrival_station_code = scrapy.Field()
  duration_readable = scrapy.Field()
  duration = scrapy.Field()
  changes = scrapy.Field()
