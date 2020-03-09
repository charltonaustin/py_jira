import json

import requests


class Jira:
  def __init__(self, auth, headers, base_url):
    self.base_url = base_url
    self.auth = auth
    self.headers = headers

  def _get_issues_(self, modifier, start_date, end_date):
    url = f"{self.base_url}/rest/api/3/search"

    query = {
      'jql': f"'{modifier}'>='{start_date}' AND '{modifier}'<='{end_date}'",
      'maxResults': '100000'
    }
    response = requests.request(
      "GET",
      url,
      headers=self.headers,
      params=query,
      auth=self.auth
    )
    text = response.text

    return json.loads(text)['issues']

  def _get_url(self, url):
    response = requests.request(
      "GET",
      url,
      headers=self.headers,
      auth=self.auth
    )
    issue = json.loads(response.text)
    return issue

  def get_users(self):
    all_users = self._get_url(f"{self.base_url}/rest/api/3/users")
    atlassian_users = [user for user in all_users if user['accountType'] == 'atlassian']
    active_users = [user for user in atlassian_users if user['active'] is True]

    return active_users

  def get_issues_updated_at(self, start_date, end_date):
    return self._get_issues_("updated", start_date, end_date)

  def get_issues_created_at(self, start_date, end_date):
    return self._get_issues_("created", start_date, end_date)

  def get_history(self, key):
    return self._get_url(f"{self.base_url}/rest/api/3/issue/{key}/changelog")

  def get_issue(self, key):
    return self._get_url(f"{self.base_url}/rest/api/3/issue/{key}")
