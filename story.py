from datetime import timedelta

SECONDS_IN_DAY = (60 * 60 * 24)


class Story:
  def __init__(self, type_, key_, summary, estimate):
    self.estimate = estimate
    self.summary = summary
    self.key_ = key_
    self.type = type_
    self.transitions = []
    self.number_of_status_changes = 0
    self.time_in_ready = timedelta()
    self.time_in_progress = timedelta()
    self.time_in_testing = timedelta()
    self.time_in_completed = timedelta()

  def add_transition(self, transition):
    self.transitions.append(transition)

  @staticmethod
  def get_time(started_at, ended_at):
    if started_at and ended_at:
      return started_at - ended_at
    return None

  def update_times(self, type_, time):
    if not (type_ and time):
      return
    if type_ == "Ready":
      self.time_in_ready += time
      return
    if type_ == "In Progress":
      self.time_in_progress += time
      return
    if type_ == "Testing":
      self.time_in_testing += time
      return
    if type_ == "Completed":
      self.time_in_completed += time
      return

  def print_csv(self):
    board, key = self.key_.split("-")
    summary = self.summary.replace(",", " ")
    new_line = f"{self.type},{board},{key},{summary},"
    date_picked_up = None
    date_deployed = None
    self.transitions = sorted(self.transitions, key=lambda t: t.created_at)
    transition_started_at = None
    transition_ended_at = None
    transition_type = None
    for transition in self.transitions:
      if transition.to_string == "In Progress" and date_picked_up is None:
        date_picked_up = transition.created_at
      time = self.get_time(transition_started_at, transition_ended_at)
      self.update_times(transition_type, time)
      transition_type = transition.to_string
      transition_ended_at = transition_started_at
      transition_started_at = transition.created_at
      self.number_of_status_changes += 1

    for transition in reversed(self.transitions):
      if transition.to_string == "Deployed":
        date_deployed = transition.created_at
        break
    if date_picked_up:
      new_line += f"{date_picked_up.strftime('%Y-%m-%d')},"
    else:
      new_line += f"{date_picked_up},"
    if date_deployed:
      new_line += f"{date_deployed.strftime('%Y-%m-%d')},"
    else:
      new_line += f"{date_deployed},"
    time_in_ready = round(self.time_in_ready.total_seconds() / SECONDS_IN_DAY, 2)
    time_in_progress = round(self.time_in_progress.total_seconds() / SECONDS_IN_DAY, 2)
    time_in_testing = round(self.time_in_testing.total_seconds() / SECONDS_IN_DAY, 2)
    time_in_completed = round(self.time_in_completed.total_seconds() / SECONDS_IN_DAY, 2)
    new_line += f"{self.number_of_status_changes},"
    new_line += f"{time_in_ready},"
    new_line += f"{time_in_progress},"
    new_line += f"{time_in_testing},"
    new_line += f"{time_in_completed},"
    new_line += f"{self.estimate},"
    total_time_sum = sum([time_in_ready, time_in_progress, time_in_testing, time_in_completed])
    total_time_sum = round(total_time_sum, 2)
    new_line += f"{total_time_sum},"
    total_time_diff = 0
    if date_picked_up and date_deployed:
      total_time_diff = round((date_deployed - date_picked_up).days, 2)
    new_line += f"{(total_time_diff)},"
    difference = 0
    if self.estimate and total_time_diff:
      difference = total_time_diff - self.estimate
    new_line += f"{difference}"
    print(new_line)
