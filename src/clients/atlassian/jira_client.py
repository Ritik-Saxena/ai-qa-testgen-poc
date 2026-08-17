import os

from requests.auth import HTTPBasicAuth
from jira import JIRA
from jira.exceptions import JIRAError

class JiraClient:
    def __init__(self):
        self.ATLASSIAN_BASE_URL = os.getenv("Atlassian_BASE_URL")
        self.ATLASSIAN_EMAIL = os.getenv("Atlassian_EMAIL")
        self.ATLASSIAN_API_TOKEN = os.getenv("Atlassian_API_TOKEN")

        self.auth = HTTPBasicAuth(self.ATLASSIAN_EMAIL, self.ATLASSIAN_API_TOKEN)

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def _jira_field_value(self, field):
        if field is None:
            return None

        if isinstance(field, list):
            return [self._jira_field_value(item) for item in field]

        if isinstance(field, dict):
            for key in ("value", "name", "displayName"):
                if key in field:
                    return field[key]
            return field

        for attr in ("value", "name", "displayName"):
            value = getattr(field, attr, None)
            if value is not None:
                return value

        return field


    def _issue_field(self, fields, field_name):
        return self._jira_field_value(getattr(fields, field_name, None))

    
    def fetch_user_story_jira(self, issue_key):
        jira = JIRA(
            server=self.ATLASSIAN_BASE_URL,
            basic_auth=(self.ATLASSIAN_EMAIL, self.ATLASSIAN_API_TOKEN),
        )

        try:
            issue = jira.issue(issue_key)
        except JIRAError as e:
            return {"Error": f"Jira ticket {issue_key} is not valid or not accessible.", "Error Message": f"{str(e.text)}", "valid": False} 

        story_id = issue.key
        summary = self._issue_field(issue.fields, "summary")
        description = self._issue_field(issue.fields, "description")
        application_context = {
            "application_url": self._issue_field(issue.fields, "customfield_10042"),
            "module": self._issue_field(issue.fields, "customfield_10047"),
            "environment": self._issue_field(issue.fields, "customfield_10048"),
            "platform": self._issue_field(issue.fields, "customfield_10046")
        }
        preconditions = self._issue_field(issue.fields, "customfield_10041")
        acceptance_criteria = self._issue_field(issue.fields, "customfield_10039")
        constraints_assumptions = self._issue_field(issue.fields, "customfield_10043")
        severity = self._issue_field(issue.fields, "customfield_10044")
        pull_request = self._issue_field(issue.fields, "customfield_10040")

        return {
            "story_id": story_id,
            "summary": summary,
            "description": description,
            "application_context": application_context,
            "preconditions": preconditions,
            "acceptance_criteria": acceptance_criteria,
            "constraints_assumptions": constraints_assumptions,
            "severity": severity,
            "pull_request": pull_request
        }
    
    def add_comment_to_ticket(self, issue_key, comment):
        jira = JIRA(
            server=self.ATLASSIAN_BASE_URL,
            basic_auth=(self.ATLASSIAN_EMAIL, self.ATLASSIAN_API_TOKEN),
        )

        try:
            issue = jira.issue(issue_key)
        except JIRAError as e:
            return {"Error": f"Jira ticket {issue_key} is not valid or not accessible.", "Error Message": f"{str(e.text)}", "valid": False} 
        
        jira.add_comment(issue, comment)
