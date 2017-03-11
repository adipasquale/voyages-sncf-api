import requests
from models.round_trip import RoundTrip
# import gevent


SCRAPYRT_ENDPOINT = "http://localhost:9080/crawl.json"


class ScrapyRTClient(object):

  @staticmethod
  def get_rides(
    departure_city, arrival_city, departure_date, precise_departure_time, price_below
  ):
    r = requests.get(SCRAPYRT_ENDPOINT, params={
      "departure_city": departure_city,
      "arrival_city": arrival_city,
      "departure_date": departure_date.strftime("%d/%m/%Y"),
      "precise_departure_time": precise_departure_time,
      "price_below": price_below
    })

    return r.json()["items"]

  # @staticmethod
  # def get_round_trip(
  #   departure_city, arrival_city, departure_date, return_date
  # ):
  #   outward_rides_greenlet = gevent.spawn(
  #     ScrapyRTClient.get_rides,
  #     departure_city, arrival_city, departure_date
  #   )
  #   return_rides_greenlet = gevent.spawn(
  #     ScrapyRTClient.get_rides,
  #     arrival_city, departure_city, return_date
  #   )

  #   gevent.joinall([outward_rides_greenlet, return_rides_greenlet])

  #   return RoundTrip(
  #     departure_date, return_date,
  #     outward_rides_greenlet.value,
  #     return_rides_greenlet.value
  #   )
