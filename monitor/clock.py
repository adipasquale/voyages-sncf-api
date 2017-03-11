#!/usr/local/bin/python

import schedule
import time
from agent import Agent

agent = Agent()

schedule.every(1).minutes.do(agent.check_all_tickets)

time.sleep(5)  # initial sleep so scrapyrt wakes up

while True:
  schedule.run_pending()
  time.sleep(1)
