class DateRange:
  def __init__(self, start_date, end_date):
    self.start_date = start_date
    self.end_date = end_date

  def in_range(self, date):
    in_range = False
    try:
      in_range = self.start_date <= date <= self.end_date
    except TypeError:
      in_range = self.start_date <= date.date() <= self.end_date

    return in_range
