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
# from copy import copy


class VoyagesSncfComSpider(scrapy.Spider):
  name = "voyagessncf_com"
  allowed_domains = ["voyages-sncf.com"]
  command_line_args = {}
  params = {}
  custom_settings = {
    'COOKIES_ENABLED': True
  }
  ROOT_URL = "http://www.voyages-sncf.com//vsc/train-ticket/"

  def __init__(self, *args, **kwargs):
    # entry point 1/2 for CLI calls `scrapy crawl`
    self.command_line_args = kwargs

  def start_requests(self):
    # entry point 2/2 for CLI calls `scrapy crawl`
    self.params = self.parse_params(self.command_line_args)
    url = "%s?%s" % (self.ROOT_URL, urllib.urlencode(self.build_get_params()))
    yield scrapy.Request(url)

  def modify_realtime_request(self, request):
    # entry point for scrapyrt API calls
    self.params = self.parse_params(request.meta)
    url = "%s?%s" % (self.ROOT_URL, urllib.urlencode(self.build_get_params()))
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

      if self.params.get("card") == "HAPPY_CARD" and "SEMIFLEX" not in r["priceProposals"]:
        continue  # filter out lines without a 'modifiable' price

      arrival_datetime = dateutil.parser.parse(r["arrivalDate"])
      offer = Offer()
      offer["price"] = r["priceProposals"]["SEMIFLEX"]["amount"]
      offer["remaining_seats"] = r["priceProposals"]["SEMIFLEX"]["remainingSeat"]

      departure_datetime = dateutil.parser.parse(r["departureDate"])
      offer["departure_datetime"] = departure_datetime
      offer["departure_time_readable"] = departure_datetime.strftime("%H:%M")
      offer["arrival_datetime"] = arrival_datetime
      offer["arrival_time_readable"] = arrival_datetime.strftime("%H:%M")

      offer["departure_station"] = r["origin"]
      offer["departure_station_code"] = r["originCode"]
      offer["arrival_station"] = r["destination"]
      offer["arrival_station_code"] = r["destinationCode"]

      # offer["original"] = copy(r)

      if len(r["segments"]) == 1:
        minutes_total = r["segments"][0]["duration"] / 1000 / 60
        duration = timedelta(minutes=minutes_total)
        hours, rem = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        offer["duration_readable"] = "%sh%s" % (hours, minutes)
        offer["duration"] = minutes_total

      if self.params.get("departure_hour") and departure_datetime.hour < int(self.params["departure_hour"]):
        continue
        # voyages-sncf always takes 1H less than you ask, and it returns all the times
        # of the day when there's no results after you hour

      if self.params.get("precise_departure_time") and \
         self.params["precise_departure_time"].upper().replace("H",":") != departure_datetime.strftime("%H:%M"):
          continue

      if "price_below" in self.params and offer["price"] > self.params["price_below"]:
        continue

      yield offer

  def parse_params(self, params):
    now = datetime.now(pytz.timezone("Europe/Paris"))
    if params.get("departure_date") == now.strftime("%d/%m/%Y"):
      params.setdefault("departure_hour", now.hour)
    else:
      params.setdefault("departure_hour", 6)

    if params.get("card") == "TGV_MAX" or params.get("card") == "TGVMAX":
      params["card"] = "HAPPY_CARD"

    if params.get("card") == "HAPPY_CARD":
      params.setdefault("card_number", "HC600069953")
      params.setdefault("birth_date", "14/03/1991")

    for p in ["departure_hour", "price_below"]:
      if p in params:
        params[p] = int(params[p])

    return params

  def build_get_params(self):
    return {
      '_LANG': 'fr',
      'ORIGIN_CITY_CHECK': '',
      'ORIGIN_CITY_RR_CODE': '',
      'ORIGIN_CITY': self.params.get("departure_city"),

      'DESTINATION_CITY_CHECK': '',
      'DESTINATION_CITY': self.params.get("arrival_city"),
      'DESTINATION_CITY_RR_CODE': '',

      'OUTWARD_SCHEDULE_TYPE': 'DEPARTURE_FROM',
      'OUTWARD_DATE': self.params.get("departure_date"),
      'OUTWARD_TIME': self.params.get("departure_hour") + 1,
      'INWARD_DATE': '',
      'INWARD_TIME': '',
      'COMFORT_CLASS': '2',
      'DISTRIBUTED_COUNTRY': 'FR',
      'PASSENGER_1': '100005891955',
      'PASSENGER_1_CARD': self.params.get("card"),
      'PASSENGER_1_FID_PROG': '',
      'PASSENGER_1FID_NUM_BEGIN': '',
      'CODE_PROMO_1': '',
      'PASSENGER_1_CARD_NUMBER': self.params.get("card_number"),
      'PASSENGER_1_CARD_BIRTH_DATE': self.params.get("birth_date"),
      'action:searchTravelLaunchTrain': 'Rechercher'
    }
