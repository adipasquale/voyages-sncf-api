#!/usr/local/bin/python

import schedule
import time
import sys
import os
from agent import Agent
from utils.bug_tracker import BugTracker


agent = Agent()

schedule.every(1).minutes.do(agent.check_all_tickets)

time.sleep(5)  # initial sleep so scrapyrt wakes up

sys.excepthook = BugTracker().handle_exception

while True:
  schedule.run_pending()
  time.sleep(1)
