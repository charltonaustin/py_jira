import os
from datetime import datetime

from requests.auth import HTTPBasicAuth

from api import Jira
from transition import Transition, Story


def get_issue_history(api, story, issue):
  values = api.get_history(issue['key'])['values']
  for value in values:
    for item in value['items']:
      if item['field'] == 'status':
        t = Transition(
          value['author']['displayName'],
          item["fromString"],
          item["toString"],
          datetime.strptime(value['created'], "%Y-%m-%dT%H:%M:%S.%f%z")
        )
        story.add_transition(t)


def issue_has_fields(issue):
  try:
    name = issue["fields"]["issuetype"]["name"]
    key_ = issue['key']
    summary = issue["fields"]["summary"]
    estimate = issue["fields"]["customfield_10016"]
    return True
  except KeyError:
    return None


def main():
  password = os.getenv('JIRA_AUTH')
  if not password:
    print("missing JIRA_AUTH please set environment variable")
    return

  base_url = os.getenv("JIRA_BASE_URL")

  auth = HTTPBasicAuth("charlie@tuesdaycompany.com", password)

  headers = {
    "Accept": "application/json"
  }
  api = Jira(auth, headers, base_url)
  if not password:
    print("missing JIRA_AUTH please set environment variable")
  stories = []
  keys = range(1, 733)
  print("getting story data")
  for key in keys:
    issue = api.get_issue(f"ENG-{key}")
    if not issue_has_fields(issue):
      continue
    story = Story(
      issue["fields"]["issuetype"]["name"],
      issue['key'],
      issue["fields"]["summary"],
      issue["fields"]["customfield_10016"]
    )
    get_issue_history(api, story, issue)
    stories.append(story)
  first_line = f"type,key,summary,estimate,start,end,status_changes,in_ready,"
  first_line += f"in_progress,in_testing,in_completed"
  print(first_line)
  for story in stories:
    story.print_csv()


if __name__ == "__main__":
  main()
