import requests
import os
from bug_tracker import BugTracker
import sys

class CrawlError(Exception):
  pass


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

    res = r.json()

    if res.get("errors"):
      BugTracker().handle_exception(CrawlError, res["errors"][0])
      sys.exit("got CrawlError")

    return res["items"]
