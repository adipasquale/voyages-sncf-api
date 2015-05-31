import scrapy
from voyagessncf.items import Offer
import urlparse


def get_url(rel_url, response):
  return urlparse.urljoin(response.url, rel_url)


class VoyagesSncfSpider(scrapy.Spider):
  name = "voyagessncf"
  allowed_domains = ["voyages-sncf.mobi"]

  def start_requests(self):
    return [
      scrapy.Request(
        "http://voyages-sncf.mobi", callback=self.do_search)
    ]

  def do_search(self):
    form_req = scrapy.FormRequest(
      'http://voyages-sncf.mobi/reservation/selectTravel.action?search=',
      headers={
        'Bk-Ajax': 'application/xml',
        'Origin': 'http://voyages-sncf.mobi',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'fr',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'Referer': 'http://voyages-sncf.mobi/',
        'Connection': 'keep-alive',
      },
      formdata='originCode=&originName=paris&destinationCode=&destinationName=amsterdam&outwardJourneyDate=0506&outwardJourneyHour=15&inwardJourneyDate=&inwardJourneyHour=7&travelClass=SECOND&nbBaby=0&nbChild=0&nbYouth=1&nbAdult=0&nbSenior=0',
      callback=self.parse_offer
    )
    return [form_req]

  def parse_offer(self, response):
    for item in response.css(".bk-headline.labelInDiv"):
      offer = Offer()
      offer["price"] = response.css('.results_prix::text').extract()[0].strip()
      yield offer
