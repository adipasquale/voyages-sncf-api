import requests
import os


class ScrapyRTClient(object):

  @staticmethod
  def get_rides(
    departure_city, arrival_city, departure_date, precise_departure_time, price_below, card
  ):
    r = requests.get(
      "http://%s:%s/crawl.json" % (
        os.environ["SCRAPYRT_HOST"],
        os.environ.get("SCRAPYRT_PORT", os.environ.get("PORT")),
      ),
      params={
        "departure_city": departure_city,
        "arrival_city": arrival_city,
        "departure_date": departure_date.strftime("%d/%m/%Y"),
        "precise_departure_time": precise_departure_time,
        "price_below": price_below,
        "card": card
      }
    )

    return r.json()["items"]
