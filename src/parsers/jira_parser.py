from src.clients.atlassian.jira_client import JiraClient

class JiraParser:

    def normalize_multiline_text(self, text):
        if not text:
            return []

        if isinstance(text, list):
            return text

        if not isinstance(text, str):
            text = str(text)
        
        cleaned_lines = []

        for line in text.split("\n"):
            stripped_line = line.strip()
            
            if len(stripped_line) != 0:
                cleaned_lines.append(stripped_line)

        return cleaned_lines


    def jira_issue_json(self, issue_key):
        jira_client = JiraClient();
        jira_story = jira_client.fetch_user_story_jira(issue_key)

        if jira_story.get("valid") is False:
            return jira_story
        

        story_id = jira_story.get("story_id")
        summary = self.normalize_multiline_text(jira_story.get("summary"))
        description = self.normalize_multiline_text(jira_story.get("description"))
        application_context = jira_story.get("application_context")
        preconditions = self.normalize_multiline_text(jira_story.get("preconditions"))
        acceptance_criteria = self.normalize_multiline_text(jira_story.get("acceptance_criteria"))
        constraints_assumptions = self.normalize_multiline_text(jira_story.get("constraints_assumptions"))
        severity = self.normalize_multiline_text(jira_story.get("severity"))
        pull_request = self.normalize_multiline_text(jira_story.get("pull_request"))

        jira_story_json = {
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

        filtered_jira_story_json = {k: v for k, v in jira_story_json.items() if v} # filtering empty fields to reduce token size & noise for LLM analysis

        return filtered_jira_story_json
