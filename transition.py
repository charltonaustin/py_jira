class Transition:
  def __init__(self, author, from_string, to_string, created_at):
    self.created_at = created_at
    self.to_string = to_string
    self.from_string = from_string
    self.author = author

  def get_transition_type(self):
    return self.to_string
