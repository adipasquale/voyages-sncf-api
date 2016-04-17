

class RoundTrip(object):

  def __init__(self, departure_date, return_date, outward_rides, return_rides):
    self.departure_date = departure_date
    self.return_date = return_date
    self.outward_rides = outward_rides
    self.return_rides = return_rides
    self.outward_rides_sorted = sorted(outward_rides, key=lambda r: r["price"])
    self.return_rides_sorted = sorted(return_rides, key=lambda r: r["price"])

  def to_json(self):
    return {
      "week_number": self.departure_date.isocalendar()[1],
      "outward_rides": self.outward_rides,
      "return_rides": self.outward_rides,
      "best_rides": {
        "outwards": self.outward_rides_sorted[0],
        "backwards": self.return_rides_sorted[0],
        "price": (
          self.outward_rides_sorted[0]["price"] +
          self.return_rides_sorted[0]["price"]
        )
      }
    }
