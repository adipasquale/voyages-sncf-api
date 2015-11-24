import scrapy
from voyagessncf.items import Offer
import urlparse
from scrapy.utils.response import open_in_browser
from scrapy.shell import inspect_response
import re
import datetime

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

  # def __init__(self, origin_name=None, destination_name=None, journey_date=None, journey_hour=None, request_id=None, *args, **kwargs):
    # super(VoyagesSncfSpider, self).__init__(**kwargs)
    # self.request_id = request_id

    # parsed_date = datetime.datetime.strptime(journey_date, "%Y-%m-%d").date() if journey_date else datetime.date.today()
    # if parsed_date < datetime.date.today():
    #   raise Exception("journey_date has to be at least one hour from now")
    # self.journey_date = parsed_date.strftime(DATE_FORMAT)

    # self.journey_hour = journey_hour or datetime.datetime.now().strftime(HOUR_FORMAT)

    # if not origin_name or not destination_name:
    #   raise Exception("no origin_name or destination_name or invalid")
    # self.origin_name = origin_name
    # self.destination_name = destination_name

    # self.travellers = {
    #   "babies": kwargs.get("babies", 0),
    #   "children": kwargs.get("children", 0),
    #   "youngs": kwargs.get("youngs", 0),
    #   "adults": kwargs.get("adults", 0),
    #   "seniors": kwargs.get("seniors", 0),
    # }
    # if sum(self.travellers.values()) == 0:
    #   self.travellers["adults"] = 1

  # def modify_realtime_request(self, request):
    # request.url = ROOT_URL
    # request.callback = self.do_search
    # return request

  # def start_requests(self):
  #   return [
  #     scrapy.Request(
  #       ROOT_URL, callback=self.do_search)
  #   ]

  def do_search(self, response):
    journey_date = response.meta.get("journey_date")
    journey_hour = response.meta.get("journey_hour")
    origin_name = response.meta.get("origin_name")
    destination_name = response.meta.get("destination_name")
    kwargs = response.meta

    parsed_date = datetime.datetime.strptime(journey_date, "%Y-%m-%d").date() if journey_date else datetime.date.today()
    if parsed_date < datetime.date.today():
      raise Exception("journey_date has to be at least one hour from now")
    self.journey_date = parsed_date.strftime(DATE_FORMAT)

    self.journey_hour = journey_hour or datetime.datetime.now().strftime(HOUR_FORMAT)

    if not origin_name or not destination_name:
      raise Exception("no origin_name or destination_name or invalid")
    self.origin_name = origin_name
    self.destination_name = destination_name

    self.travellers = {
      "babies": kwargs.get("babies", 0),
      "children": kwargs.get("children", 0),
      "youngs": kwargs.get("youngs", 0),
      "adults": kwargs.get("adults", 0),
      "seniors": kwargs.get("seniors", 0),
    }
    if sum(self.travellers.values()) == 0:
      self.travellers["adults"] = 1

    submit_url = ROOT_URL + response.css("form::attr(action)").extract()[0]
    form_req = scrapy.FormRequest(
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
        'originName': "%s" % self.origin_name.upper(),
        'destinationCode': '',
        'destinationName': "%s" % self.destination_name.upper(),
        'outwardJourneyDate': self.journey_date,
        'outwardJourneyHour': self.journey_hour,
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
    )
    return [form_req]

  def next_page(self, response):
    # open_in_browser(response)
    # inspect_response(response, self)

    return self.parse(response)

  def parse(self, response):
    response.selector.remove_namespaces()

    # open_in_browser(response)
    # inspect_response(response, self)

    for item in response.css(".journeysJourney"):
      offer = Offer()
      price_full_text = get_inner_text(item.css('.results_prix')[0])
      price_text = re.search(r"([0-9]+\,?[0-9]*)", price_full_text).groups()[0]
      price_text = price_text.replace(",", ".")
      offer["price"] = float(price_text)

      header = item.css(".bk-dv")[0]
      hours = [get_inner_text(it) for it in
               header.css('span[style="color:#E75C24;"]')]
      offer["departure_time"], offer["arrival_time"], offer["duration"] = hours

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

    link_next = response.css('[style="text-align:right;"] .bk-navlink')
    if link_next:
      url_next = link_next[0].xpath("@href").extract()[0]
      url_next = get_url(url_next, response)
      yield scrapy.Request(url_next, callback=self.next_page)
