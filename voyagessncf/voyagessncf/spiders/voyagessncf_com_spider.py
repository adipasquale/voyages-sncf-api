#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
from voyagessncf.items import Offer
import urlparse
from scrapy.utils.response import open_in_browser
from scrapy.shell import inspect_response
import re
from datetime import datetime, date, time, timedelta
import pytz
import urllib
import json
import demjson
import dateutil.parser


class VoyagesSncfComSpider(scrapy.Spider):
  name = "voyagessncf_com"
  allowed_domains = ["voyages-sncf.com"]
  command_line_args = {}
  custom_settings = {
    'COOKIES_ENABLED': True
  }
  ROOT_URL = "http://www.voyages-sncf.com//vsc/train-ticket/"

  def __init__(self, *args, **kwargs):
    # entry point 1/2 for CLI calls `scrapy crawl`
    self.command_line_args = kwargs

  def start_requests(self):
    # entry point 2/2 for CLI calls `scrapy crawl`
    get_params = self.build_get_params(self.command_line_args)
    url = "%s?%s" % (self.ROOT_URL, urllib.urlencode(get_params))
    yield scrapy.Request(url)

  def modify_realtime_request(self, request):
    # entry point for scrapyrt API calls
    get_params = self.build_get_params(request.meta)
    url = "%s?%s" % (self.ROOT_URL, urllib.urlencode(get_params))
    return scrapy.Request(url)

  def parse(self, response):
    # this is the callback to the ROOT_URL response : the please wait page
    url_query_string = urlparse.urlparse(response.url).query
    parsed_query = urlparse.parse_qs(url_query_string)
    search_id = parsed_query['hid'][0]
    print("yielding search with %s" % search_id)
    yield scrapy.Request(
      "http://www.voyages-sncf.com/vsc/proposals/findProposals?hid=%s" % search_id,
      self.parse_results
    )

  def parse_results(self, response):
    text_body = str(response.body)

    for line in text_body.split("\n"):
      if line.strip().startswith("data.searchResponse = JSON"):
        json_data = re.findall(r"JSON\.parse\('(.*)'\)", line.strip())[0]
        json_data = json_data.replace('\\"', '"')
        json_data = demjson.decode((json_data))

    json_data["status"] == "SUCCESS"

    results = json_data["results"]

    for r in results:
      if r["pushProposal"]:
        continue  # filter out bus

      departure_datetime = dateutil.parser.parse(r["departureDate"])
      arrival_datetime = dateutil.parser.parse(r["arrivalDate"])
      p = r
      offer = Offer()
      offer["price"] = p["priceProposals"]["SEMIFLEX"]["amount"]

      offer["departure_datetime"] = departure_datetime
      offer["departure_time_readable"] = departure_datetime.strftime("%H:%M")
      offer["arrival_datetime"] = arrival_datetime
      offer["arrival_time_readable"] = arrival_datetime.strftime("%H:%M")

      offer["departure_station"] = r["origin"]
      offer["departure_station_code"] = r["originCode"]
      offer["arrival_station"] = r["destination"]
      offer["arrival_station_code"] = r["destinationCode"]

      if len(r["segments"]) == 1:
        minutes_total = r["segments"][0]["duration"] / 1000 / 60
        duration = timedelta(minutes=minutes_total)
        hours, rem = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        offer["duration_readable"] = "%sh%s" % (hours, minutes)
        offer["duration"] = minutes_total

      yield offer

  def build_get_params(self, params):
    return {
      '_LANG': 'fr',
      'ORIGIN_CITY_CHECK': '',
      'ORIGIN_CITY_RR_CODE': '',
      'ORIGIN_CITY': params.get("departure_city"),

      'DESTINATION_CITY_CHECK': '',
      'DESTINATION_CITY': params.get("arrival_city"),
      'DESTINATION_CITY_RR_CODE': '',

      'OUTWARD_SCHEDULE_TYPE': 'DEPARTURE_FROM',
      'OUTWARD_DATE': params.get("departure_date"),
      'OUTWARD_TIME': params.get("departure_hour"),
      'INWARD_DATE': '',
      'INWARD_TIME': '',
      'COMFORT_CLASS': '2',
      'DISTRIBUTED_COUNTRY': 'FR',
      'PASSENGER_1': '100005891954',
      'PASSENGER_1_CARD': params.get("card"),
      'PASSENGER_1_FID_PROG': '',
      'PASSENGER_1FID_NUM_BEGIN': '',
      'CODE_PROMO_1': '',
      'PASSENGER_1_CARD_NUMBER': params.get("card_number"),
      'PASSENGER_1_CARD_BIRTH_DATE': params.get("birth_date"),
      'action:searchTravelLaunchTrain': 'Rechercher'
    }
