#!/usr/local/bin/python

from datetime import datetime
from airtable import airtable
from utils.scrapyrt_client import ScrapyRTClient
from utils.notifier import Notifier
import pytz
import os
import locale
import re

locale.setlocale(locale.LC_TIME, os.environ["TIME_LOCALE"])

class Agent(object):

  phone_regexes = {"0": re.compile(r"^0"), "+": re.compile(r"^\+")}
  TZ = pytz.timezone("Europe/Paris")

  def __init__(self):
    self.airtable_client = airtable.Airtable(
      os.environ["AIRTABLE_BASE_ID"],
      os.environ["AIRTABLE_API_KEY"]
    )
    self.notifier = Notifier()

  def check_all_tickets(self):
    ticket_records = self.airtable_client.get(
      os.environ["AIRTABLE_TABLE_NAME_MONITORED"],
      filter_by_formula='state = "monitoring"'
    )["records"]

    user_records = self.airtable_client.get(
      os.environ["AIRTABLE_TABLE_NAME_USERS"]
    )["records"]
    users_by_id = {r["id"]: r for r in user_records}

    for ticket_record in ticket_records:
      user_record = users_by_id[ticket_record["fields"]["user"][0]]
      self.check_ticket(ticket_record, user_record)

  def check_ticket(self, ticket_record, user_record):
    ticket = ticket_record["fields"]
    user = user_record["fields"]
    departure_datetime = datetime.strptime(
      "%s-%s" % (ticket["departure_date"], ticket["precise_departure_time"]),
      "%Y-%m-%d-%H:%M"
    )
    departure_datetime = Agent.TZ.localize(departure_datetime)

    if departure_datetime <= datetime.now(Agent.TZ):
      print "marking ticket not_found because departure is in the past (%s < %s)" % (
        departure_datetime.strftime("%H:%M"), datetime.now(Agent.TZ).strftime("%H:%M")
      )
      self.update_ticket(ticket_record, {"state": "not_found"})
      return

    results = ScrapyRTClient.get_rides(
      departure_city=ticket["departure_city"],
      arrival_city=ticket["arrival_city"],
      departure_date=departure_datetime,
      precise_departure_time=ticket["precise_departure_time"],
      price_below=ticket["price_below"],
      card=user["card"]
    )

    if len(results) > 0:
      text = "%s -> %s le %s a %s dispo pour moins de %s euros !" % (
        ticket["departure_city"],
        ticket["arrival_city"],
        departure_datetime.strftime("%A %d/%m").lower(),
        ticket["precise_departure_time"],
        ticket["price_below"],
      )
      phone_number = user["phone_number"]
      phone_number = re.sub(Agent.phone_regexes["0"], "33", phone_number)
      phone_number = re.sub(Agent.phone_regexes["+"], "", phone_number)

      if os.environ.get("SMS_ENABLED"):
        print("sending SMS '%s' to %s ..." % (text, phone_number))
        self.notifier.notify(phone_number, text)
      else:
        print("would have sent SMS '%s' to %s" % (text, phone_number))

      self.update_ticket(ticket_record, {
        "state": "found",
        "found_at": datetime.now(Agent.TZ).isoformat()
      })

  def update_ticket(self, ticket_record, updates):
    res = self.airtable_client.update(
      os.environ["AIRTABLE_TABLE_NAME_MONITORED"],
      str(ticket_record["id"]),
      updates
    )
    if res.get("error"):
      raise Exception("could not update ticket_record")


if __name__ == '__main__':
  Agent().check_all_tickets()
