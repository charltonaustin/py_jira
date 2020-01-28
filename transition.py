from datetime import timedelta


class Transition:
  def __init__(self, author, from_string, to_string, created_at):
    self.created_at = created_at
    self.to_string = to_string
    self.from_string = from_string
    self.author = author

  def get_transition_type(self):
    return self.to_string


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
    new_line = f"{self.type},{self.key_},'{self.summary}',{self.estimate},"
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
    new_line += f"{self.number_of_status_changes},"
    new_line += f"{self.time_in_ready.total_seconds()},"
    new_line += f"{self.time_in_progress.total_seconds()},"
    new_line += f"{self.time_in_testing.total_seconds()},"
    new_line += f"{self.time_in_completed.total_seconds()}"
    print(new_line)