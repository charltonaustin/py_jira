class User:
  def __init__(self, account_id):
    self.account_id = account_id
    self.display_name = None
    self.activities = []

  def set_display_name(self, name):
    self.display_name = name

  def add_activity(self, activity):
    self.activities.append(activity)

  def print_activity(self):
    activities = sorted(self.activities, key=lambda a: a.date)
    print(f"display name: {self.display_name}, account id: {self.account_id}")
    print("key,summary,from,to,date")
    for activity in activities:
      print_string = ""
      print_string += activity.key + ","
      print_string += activity.summary + ","
      print_string += activity.from_string + ","
      print_string += activity.to_string + ","
      print_string += str(activity.date.date())
      print(print_string)
