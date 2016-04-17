from flask import Flask
from flask import request
from flask import jsonify
from utils.scrapyrt_client import ScrapyRTClient
from datetime import datetime, date, timedelta
import gevent

app = Flask(__name__)

@app.route("/")
def hello():
  return "Hello World!"


@app.route("/api/v1/rides/search")
def search_rides():
  if not (request.args.get("departureCity") and
          request.args.get("arrivalCity") and
          request.args.get("departureDate")):
    raise Exception("missing args")

  departure_date = datetime.strptime(datetime.date.today(), "%d/%m/%Y")

  rides = ScrapyRTClient.get_rides(
    request.args["departureCity"],
    request.args["arrivalCity"],
    departure_date,
  )

  return jsonify(results=rides)

def next_weekday(d, weekday):
  days_ahead = weekday - d.weekday()
  if days_ahead <= 0: # Target day already happened this week
    days_ahead += 7
  return d + timedelta(days_ahead)

@app.route("/api/v1/round_trips/search")
def search_weekends():
  if not (request.args.get("departureCity") and
          request.args.get("arrivalCity")):
    raise Exception("missing args")

  greenlets = []

  for delta in [0, 1]:
    departure_date = date.today() + timedelta(days=7 * delta)
    friday = next_weekday(departure_date, 4)
    sunday = next_weekday(departure_date, 6)

    greenlets.append(gevent.spawn(
      ScrapyRTClient.get_round_trip,
      request.args["departureCity"],
      request.args["arrivalCity"],
      friday, sunday
    ))

  gevent.joinall(greenlets)
  round_trips = [g.value for g in greenlets]

  return jsonify(
    results=[rt.to_json() for rt in round_trips],
    success=True
  )

if __name__ == "__main__":
  app.run(debug=True)
