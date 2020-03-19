import argparse
import datetime
import os
import sys

from requests.auth import HTTPBasicAuth

from activity import Activity
from api import Jira
from date_range import DateRange
from story import Story
from transition import Transition
from user import User


def get_issue_history(api, story, issue):
  values = api.get_history(issue["key"])["values"]
  for value in values:
    for item in value["items"]:
      if item["field"] == "status":
        t = Transition(
          value["author"]["displayName"],
          item["fromString"],
          item["toString"],
          datetime.datetime.strptime(value["created"], "%Y-%m-%dT%H:%M:%S.%f%z")
        )
        story.add_transition(t)


def issue_has_fields(issue):
  try:
    name = issue["fields"]["issuetype"]["name"]
    key_ = issue["key"]
    summary = issue["fields"]["summary"]
    estimate = issue["fields"]["customfield_10016"]
    return True
  except KeyError:
    return None


def get_or_exit(env_name):
  env = os.getenv(env_name)
  if not env:
    print(f"missing {env_name} please set environment variable")
    sys.exit(1)
  return env


def main():
  parser = argparse.ArgumentParser(
    description="gather jira data",
    usage=f"{os.path.basename(__file__)} -s 16-Jul-2020 -e 20-Jul-2020"
  )

  parser.add_argument(
    "-sd",
    "--start",
    dest="start_date",
    metavar="Start date for analysis. Defaults to last week.",
    type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d").date(),
    nargs=1,
    help="The first day inclusive of analysis. ex: 16-Jul-2020",
    default=[(datetime.datetime.today() - datetime.timedelta(days=7)).date()]
  )

  parser.add_argument(
    "-ed",
    "--end",
    dest="end_date",
    metavar="End date for analysis. Defaults to today.",
    type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d").date(),
    nargs=1,
    help="The last day inclusive of analysis. ex: 16-Jul-2020",
    default=[datetime.datetime.today().date()]
  )


  parser.add_argument(
    "-si",
    "--issue_start",
    dest="issue_start",
    metavar="First jira ticket number",
    type=int,
    help="The first jira ticket number. ex: 1",
    default=1
  )

  parser.add_argument(
    "-ei",
    "--issue_end",
    dest="issue_end",
    metavar="The last jira ticket number.",
    type=int,
    help="The last jira ticket number. ex: 99",
    default=100
  )

  parser.add_argument(
    "-k",
    "--key",
    dest="key",
    metavar="Key for ticket.",
    help="The last day inclusive of analysis. ex: 16-Jul-2020",
    default="ENG"
  )

  parser.add_argument(
    "-u",
    "--user",
    action='count',
    default=0,
    help="Show all display names and accountIds.",
  )

  parser.add_argument(
    "-a",
    "--accountId",
    dest="account_id",
    help="Specify an account id to see the activity of that account id for the time period.",
    nargs=1,
    default=[]
  )

  parser.add_argument(
    "-d",
    "--displayName",
    dest="display_name",
    help="Specify a display name to see the account activity for the time period.",
    nargs="*",
    default=[],
  )

  parser.add_argument(
    "-c",
    "--csv",
    help="Print out all activity between dates as a csv.",
    action='count',
    default=0,
  )

  args = parser.parse_args()
  start = args.start_date[0]
  end = args.end_date[0]
  date_range = DateRange(start, end)
  api = create_api()
  if args.user:
    users = api.get_users()
    for user in users:
      print(user["displayName"], user["accountId"])
    return

  issues = api.get_issues_updated_at(start, end)
  if args.account_id:
    print_user_activity(api, issues, args.account_id[0], date_range)
    return

  if args.display_name:
    users = api.get_users()
    account_id = None
    display_name = " ".join(args.display_name)
    for user in users:
      if user["displayName"] == display_name:
        account_id = user["accountId"]

    if not account_id:
      print("invalid displayName please use --user to find a display name")
      return
    print_user_activity(api, issues, account_id, date_range)
    return

  if args.csv:
    issues = []
    print(f"getting {args.key}-{args.issue_start} to {args.key}-{args.issue_end}")
    for i in range(args.issue_start, args.issue_end):
      issues.append(api.get_issue(f"{args.key}-{i}"))
    print_csv(api, issues)
    return
  parser.print_help()


def print_user_activity(api, issues, account_id, date_range):
  user = User(account_id)
  for issue in issues:
    if not issue_has_fields(issue):
      continue
    get_user_activity(api, issue, account_id, date_range, user)

  user.print_activity()

def get_user_activity(api, issue, account_id, date_range, user):
  values = api.get_history(issue["key"])["values"]
  for value in values:
    for item in value["items"]:
      if item["field"] == "status":
        created = datetime.datetime.strptime(value["created"], "%Y-%m-%dT%H:%M:%S.%f%z")
        if value["author"]["accountId"] == account_id and date_range.in_range(created):
          user.set_display_name(value["author"]["displayName"])
          t = Activity(
            issue["key"],
            issue["fields"]["summary"],
            item["fromString"],
            item["toString"],
            datetime.datetime.strptime(value["created"], "%Y-%m-%dT%H:%M:%S.%f%z")
          )
          user.add_activity(t)


def print_csv(api, issues):
  stories = []
  for issue in issues:
    if not issue_has_fields(issue):
      continue
    story = Story(
      issue["fields"]["issuetype"]["name"],
      issue["key"],
      issue["fields"]["summary"],
      issue["fields"]["customfield_10016"]
    )
    get_issue_history(api, story, issue)
    stories.append(story)
  first_line = f"type,board,key,summary,start,end,status_changes,in_ready,"
  first_line += f"in_progress,in_testing,in_completed,estimate,total_time_sum,"
  first_line += f"total_time_diff,difference"
  print(first_line)
  for story in stories:
    story.print_csv()


def create_api():
  password = get_or_exit("JIRA_AUTH_PASS")
  username = get_or_exit("JIRA_AUTH_USER")
  base_url = get_or_exit("JIRA_BASE_URL")
  auth = HTTPBasicAuth(username, password)
  headers = {
    "Accept": "application/json"
  }
  api = Jira(auth, headers, base_url)
  return api


if __name__ == "__main__":
  main()
