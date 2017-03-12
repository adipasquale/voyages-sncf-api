# stopped working on this because https://github.com/scrapy/scrapy/issues/1015

from scrapy import signals

import os

try:
  import raven
  SENTRY_CLIENT = raven.Client(
    dsn=os.environ["SENTRY_DSN"],
    environment=os.environ["ENVIRONMENT"]
  )
except:
  SENTRY_CLIENT = None


class LogExceptionsMiddleware(object):

  def process_spider_exception(self, response, exception, spider):
    print "wazaaaa"
    if SENTRY_CLIENT != None:
      SENTRY_CLIENT.captureException(exc_info=(
        "yo",
        exception.args[0],
        exception.getTraceback()
      ))
