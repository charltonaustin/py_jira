import json

import requests


class Jira:
  def __init__(self, auth, headers, base_url):
    self.base_url = base_url
    self.auth = auth
    self.headers = headers

  def get_issues(self):
    url = f"{self.base_url}/rest/api/2/search"

    query = {
      'jql': f"project='ENG'",
      'maxResults': '10000'
    }

    response = requests.request(
      "GET",
      url,
      headers=self.headers,
      params=query,
      auth=self.auth
    )
    return json.loads(response.text)['issues']

  def get_history(self, key):
    return self.get_url(f"{self.base_url}/rest/api/2/issue/{key}/changelog")

  def get_url(self, url):
    response = requests.request(
      "GET",
      url,
      headers=self.headers,
      auth=self.auth
    )
    issue = json.loads(response.text)
    return issue

  def get_issue(self, key):
    return self.get_url(f"{self.base_url}/rest/api/2/issue/{key}")
