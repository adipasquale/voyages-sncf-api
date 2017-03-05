import requests
from models.round_trip import RoundTrip
import gevent


SCRAPYRT_ENDPOINT = "http://localhost:9080/crawl.json"


class ScrapyRTClient(object):

  @staticmethod
  def get_rides(
    departure_city, arrival_city, departure_date, hour="18"
  ):
    r = requests.post(SCRAPYRT_ENDPOINT, json={
      "request": {
        "url": "http://voyages-sncf.mobi",
        "meta": {
          "departure_city": departure_city,
          "arrival_city": arrival_city,
          "departure_date": departure_date.strftime("%d/%m/%Y"),
          "departure_hour": "18"
        }
      },
      "spider_name": "voyagessncf_mobi"
    })

    return r.json()["items"]

  @staticmethod
  def get_round_trip(
    departure_city, arrival_city, departure_date, return_date
  ):
    outward_rides_greenlet = gevent.spawn(
      ScrapyRTClient.get_rides,
      departure_city, arrival_city, departure_date
    )
    return_rides_greenlet = gevent.spawn(
      ScrapyRTClient.get_rides,
      arrival_city, departure_city, return_date
    )

    gevent.joinall([outward_rides_greenlet, return_rides_greenlet])

    return RoundTrip(
      departure_date, return_date,
      outward_rides_greenlet.value,
      return_rides_greenlet.value
    )
