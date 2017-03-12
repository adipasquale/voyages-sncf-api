import os


class BugTracker(object):

  def __init__(self):
    try:
      import raven
      self.client = raven.Client(
        dsn=os.environ["SENTRY_DSN"],
        environment=os.environ["ENVIRONMENT"]
      )
    except:
      print("could not load sentry client ..")
      self.client = None

  def handle_exception(self, exception_type, value, traceback=None):
    if self.client:
      self.client.captureException(exc_info=(exception_type, value, traceback))

