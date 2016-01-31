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
from copy import copy

ROOT_URL = "http://voyages-sncf.mobi"
DATE_FORMAT = '%d%m'
HOUR_FORMAT = '%H'


def get_url(rel_url, response):
  return urlparse.urljoin(response.url, rel_url)


def get_inner_text(selector):
  return "\n".join(selector.xpath("text()").extract() + selector.xpath(".//*/text()").extract()).strip()


class VoyagesSncfSpider(scrapy.Spider):
  name = "voyagessncf"
  allowed_domains = ["voyages-sncf.mobi"]
  metas = {}

  def __init__(self, *args, **kwargs):
    self.metas = kwargs

  def start_requests(self):
    yield scrapy.Request("http://voyages-sncf.mobi", self.parse, meta=self.metas)

  def get_form_request(self, url, callback, form_data_overrides={}, headers_overrides={}):
    headers = {
      'Bk-Ajax': 'application/xml',
      'Origin': 'http://voyages-sncf.mobi',
      # 'Accept-Encoding': 'gzip, deflate',
      # 'Accept-Language': 'fr',
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': '*/*',
      'Connection': 'keep-alive',
    }
    headers.update(headers_overrides)
    form_data = {
      'originCode': '',
      'originName': "%s" % self.departure_city.upper(),
      'destinationCode': '',
      'destinationName': "%s" % self.arrival_city.upper(),
      'outwardJourneyDate': self.departure_date,
      'outwardJourneyHour': self.departure_hour,
      'inwardJourneyDate': '',
      'inwardJourneyHour': '',
      'travelClass': 'SECOND',
      'nbBaby': "%s" % self.travellers["babies"],
      'nbChild': "%s" % self.travellers["children"],
      'nbYouth': "%s" % self.travellers["youngs"],
      'nbAdult': "%s" % self.travellers["adults"],
      'nbSenior': "%s" % self.travellers["seniors"],
      'back': '0',
      'modifiedODFields': '',
    }
    form_data.update(form_data_overrides)
    return scrapy.FormRequest(url, headers=headers, formdata=form_data, callback=callback)

  def parse(self, response):
    self.prepare_params(response.meta)
    submit_url = ROOT_URL + response.css("form::attr(action)").extract()[0]
    if self.commercial_card:
      return [self.get_form_request(submit_url, callback=self.more_options, form_data_overrides={"moreOptionsBtn": "+ d’options"})]
    else:
      return [self.get_form_request(submit_url, callback=self.parse_results)]

  def more_options(self, response):
    return [self.get_form_request(
      "http://voyages-sncf.mobi/reservation/selectTravel.action?search=",
      callback=self.set_commercial_card
    )]

  def set_commercial_card(self, response):
    submit_url = "https://voyages-sncf.mobi/reservation/selectOptionsMultiple.action"
    return [scrapy.FormRequest(
      submit_url,
      headers={
        # 'Bk-Ajax': 'application/xml',
        'Origin': 'http://voyages-sncf.mobi',
        # 'Accept-Encoding': 'gzip, deflate',
        # 'Accept-Language': 'fr',
        'Content-Type': 'application/x-www-form-urlencoded',
        # 'Accept': '*/*',
        'Referer': 'http://voyages-sncf.mobi/reservation/selectOptionsMultiple.action',
        'Connection': 'keep-alive',
      },
      formdata={
        'specifyAge': "false",
        # "passengers": [
        #   {
        #     "ageRank": "ADULT",
        #     "age": "",
        #     "commercialCard": self.commercial_card,
        #     "fidelityProgram": "",
        #     "fidelityNumber": ""
        #   }
        # ],
        "passengers.0.ageRank": "ADULT",
        "passengers.0.age": "",
        "passengers.0.commercialCard": self.commercial_card,
        "passengers.0.fidelityProgram": "",
        "passengers.0.fidelityNumber": "",
        "promotionCode": "",
        "submitBtn": "Continuer"
      },
      callback=self.parse_results
    )]

  def submit_search_form(self, response):
    # inspect_response(response, self)
    # open_in_browser(response)
    submit_url = ROOT_URL + response.css("form::attr(action)").extract()[0]
    return [scrapy.FormRequest(
      submit_url,
      headers={
        'Bk-Ajax': 'application/xml',
        'Origin': 'http://voyages-sncf.mobi',
        # 'Accept-Encoding': 'gzip, deflate',
        # 'Accept-Language': 'fr',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'Referer': 'http://voyages-sncf.mobi/',
        'Connection': 'keep-alive',
      },
      formdata={
        'originCode': '',
        'originName': "%s" % self.departure_city.upper(),
        'destinationCode': '',
        'destinationName': "%s" % self.arrival_city.upper(),
        'outwardJourneyDate': self.departure_date,
        'outwardJourneyHour': self.departure_hour,
        'inwardJourneyDate': '',
        'inwardJourneyHour': '',
        'travelClass': 'SECOND',
        'nbBaby': "%s" % self.travellers["babies"],
        'nbChild': "%s" % self.travellers["children"],
        'nbYouth': "%s" % self.travellers["youngs"],
        'nbAdult': "%s" % self.travellers["adults"],
        'nbSenior': "%s" % self.travellers["seniors"],
        'back': '0',
        'modifiedODFields': '',
      },
      callback=self.parse_results
    )]

  def next_page(self, response):
    # open_in_browser(response)
    # inspect_response(response, self)

    return self.parse_results(response)

  def parse_results(self, response):
    response.selector.remove_namespaces()
    tz = pytz.timezone("Europe/Paris")

    # open_in_browser(response)
    # inspect_response(response, self)

    for item in response.css(".journeysJourney"):
      offer = Offer()
      if not item.css('.results_prix'):
        continue
      price_full_text = get_inner_text(item.css('.results_prix')[0])
      price_text = re.search(r"([0-9]+\,?[0-9]*)", price_full_text).groups()[0]
      price_text = price_text.replace(",", ".")
      offer["price"] = float(price_text)

      offer["category"] = get_inner_text(item.css('.results_category')[0])

      header = item.css(".bk-dv")[0]
      hours = [get_inner_text(it) for it in
               header.css('span[style="color:#E75C24;"]')]
      offer["departure_time_readable"], offer["arrival_time_readable"], offer["duration_readable"] = hours

      departure_hour, departure_minutes = [int(i) for i in offer["departure_time_readable"].split("h")]
      arrival_hour, arrival_minutes = [int(i) for i in offer["arrival_time_readable"].split("h")]

      departure_datetime = datetime.combine(self.departure_date_parsed, time(departure_hour, departure_minutes))
      offer["departure_datetime"] = tz.localize(departure_datetime).isoformat()

      arrival_date = copy(self.departure_date_parsed)
      if arrival_hour < departure_hour:
        arrival_date += timedelta(days=1)
      arrival_datetime = datetime.combine(arrival_date, time(arrival_hour, arrival_minutes))
      offer["arrival_datetime"] = tz.localize(arrival_datetime).isoformat()

      hours, minutes = [int(i) for i in offer["duration_readable"].split("h")]
      offer["duration"] = hours * 60 + minutes

      stations = [get_inner_text(it) for it in
                  header.xpath('span[not(@style)]')]
      offer["departure_station"], offer["arrival_station"] = stations

      changes_full_text = get_inner_text(header.xpath('span[contains(text(), "chgt")]'))
      if changes_full_text:
        changes_text = re.search(r"([0-9]{1})", changes_full_text).groups()[0]
        offer["changes"] = int(changes_text)
      else:
        offer["changes"] = 0

      yield offer

    link_next = response.css('[style="text-align:right;"].bk-navlink a ')
    if link_next:
      url_next = link_next[0].xpath("@href").extract()[0]
      url_next = get_url(url_next, response)
      yield scrapy.Request(url_next, callback=self.next_page)

  def prepare_params(self, meta):
    departure_date = meta.get("departure_date")
    departure_hour = meta.get("departure_hour")
    departure_city = meta.get("departure_city")
    arrival_city = meta.get("arrival_city")

    self.departure_date_parsed = datetime.strptime(departure_date, "%d/%m/%Y").date() if departure_date else date.today()
    if self.departure_date_parsed < date.today():
      raise Exception("departure_date cannot be in the past")
    self.departure_date = self.departure_date_parsed.strftime(DATE_FORMAT)

    self.departure_hour = departure_hour or datetime.now().strftime(HOUR_FORMAT)
    self.departure_hour.replace(r"h$", "").replace(r"H$", "")

    if not departure_city or not arrival_city:
      raise Exception("no departure_city or arrival_city or invalid")
    self.departure_city = departure_city
    self.arrival_city = arrival_city

    self.travellers = {
      "babies": meta.get("babies", 0),
      "children": meta.get("children", 0),
      "youngs": meta.get("youngs", 0),
      "adults": meta.get("adults", 0),
      "seniors": meta.get("seniors", 0),
    }
    if sum(self.travellers.values()) == 0:
      self.travellers["adults"] = 1

    self.commercial_card = meta.get("commercial_card")
