import nexmo
import os


class Notifier(object):

  def __init__(self):
    self.client = nexmo.Client(
      key=os.environ.get("NEXMO_API_KEY"),
      secret=os.environ.get("NEXMO_SECRET")
    )

  def notify(self, phone_number, text):
    res = self.client.send_message({
      'from': 'TGV_HACKS',
      'to': phone_number,
      'text': text
    })

    response = res['messages'][0]

    if response['status'] == '0':
      print 'SMS sent !'
    else:
      raise Exception("could not send SMS to %s" % phone_number)

