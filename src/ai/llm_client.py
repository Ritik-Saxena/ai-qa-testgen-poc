import logging
from groq import Groq
import json
from .prompt_builder import PromptBuilder
from ..utils.json_utils import JsonUtils
from ..atlassian import confluence_client
from config import settings
from ..atlassian.jira_client import JiraClient

class LLMClient:
    MODEL = settings.LLM_MODEL
    MAX_COMPLETION_TOKENS = settings.MAX_TOKENS    # Max token size LLM model can handle per minute => (prompt tokens + meta data like temperature, role, top_p, etc. + output tokens) < 8000

    def __init__(self, jira_issue=None):
        self.promptBuilder = PromptBuilder()
        self.jira_issue = jira_issue
        self.API_KEY = settings.GROQ_API_KEY
        self.client = Groq(api_key=self.API_KEY)


    def _create_completion(self, prompt, prompt_token_size):
        final_token_size = self.MAX_COMPLETION_TOKENS - prompt_token_size - 100   # - 100 is to account for meta data tokens (temperature, role, top_p, etc.) and to have some buffer for output tokens.

        logging.info(f"\n\nPrompt Token Size: {prompt_token_size}")
        logging.info(f"Final Token Size: {final_token_size}")

        completion = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[
            {
                "role": "user",
                "content": prompt
            }
            ],
            temperature=1,
            max_completion_tokens=final_token_size,
            top_p=1,
            reasoning_effort="low",
            stream=True,
            stop=None
        )

        output = ""

        for chunk in completion:
            output += chunk.choices[0].delta.content or "" 
        
        return output


    def get_requirement_breakdown(self):
        requirement_prompt, prompt_token_size = self.promptBuilder.build_requirement_prompt(self.jira_issue)    # build_requirement_prompt returns [requirement_prompt, prompt_tokens_size]
        
        requirement_analysis_json = self._create_completion(requirement_prompt, prompt_token_size)
        
        print("requirements breakdown")

        logging.info("#################################################################")
        logging.info("#################################################################")
        logging.info("Requirement Analysis JSON Response: START")
        logging.info("#################################################################")
        logging.info("#################################################################")
        logging.info(requirement_analysis_json)
        logging.info("#################################################################")
        logging.info("#################################################################")
        logging.info("Requirement Analysis JSON Response: END")
        logging.info("#################################################################")
        logging.info("#################################################################")

        self.jsonUtils = JsonUtils(self.jira_issue)
        self.jsonUtils.json_writer(json_data=requirement_analysis_json, file_name="requirement_analysis")

        return requirement_analysis_json


    def get_testcase_generation(self, requirement_analysis_json=None):
        if requirement_analysis_json is None:
            requirement_analysis_json = self.get_requirement_breakdown()

        generate_testcase_prompt, prompt_token_size = self.promptBuilder.build_testcase_generate_prompt(requirement_analysis_json)
        
        generated_testcase_json = self._create_completion(generate_testcase_prompt, prompt_token_size)

        print("test case generation")

        logging.info("#################################################################")
        logging.info("#################################################################")
        logging.info("Test Case Generation JSON Response: START")
        logging.info("#################################################################")
        logging.info("#################################################################")
        logging.info(generated_testcase_json)
        logging.info("#################################################################")
        logging.info("#################################################################")
        logging.info("Test Case Generation JSON Response: END")
        logging.info("#################################################################")
        logging.info("#################################################################")
        
        self.jsonUtils = JsonUtils(self.jira_issue)
        self.jsonUtils.json_writer(json_data=generated_testcase_json, file_name="testcase_generation")

        return generated_testcase_json
    
    
    def get_risk_analysis(self, generated_testcase_json=None):
        if generated_testcase_json is None:
            generated_testcase_json = self.get_testcase_generation()

        risk_analysis_prompt, prompt_token_size = self.promptBuilder.build_risk_analysis_prioritization_prompt(generated_testcase_json)

        risk_analysis_result_json = self._create_completion(risk_analysis_prompt, prompt_token_size)
    
        print("risk analysis")

        logging.info("#################################################################")
        logging.info("#################################################################")
        logging.info("Risk Analysis JSON Response: START")
        logging.info("#################################################################")
        logging.info("#################################################################")
        logging.info(risk_analysis_result_json)
        logging.info("#################################################################")
        logging.info("#################################################################")
        logging.info("Risk Analysis JSON Response: END")
        logging.info("#################################################################")
        logging.info("#################################################################")
        
        self.jsonUtils = JsonUtils(self.jira_issue)
        self.jsonUtils.json_writer(json_data=risk_analysis_result_json, file_name="risk_analysis")

        return risk_analysis_result_json
    

    def get_coverage_mapping(self):
        requirement_analysis_json = self.get_requirement_breakdown()
        acceptance_criteria = json.loads(requirement_analysis_json).get("acceptance_criteria_breakdown", [])

        generated_testcase_json = self.get_testcase_generation(requirement_analysis_json)
        risk_analysis_result_json = self.get_risk_analysis(generated_testcase_json)

        coverage_mapping_prompt, prompt_token_size = self.promptBuilder.build_coverage_mapping_gap_detection_prompt(acceptance_criteria, generated_testcase_json, risk_analysis_result_json)

        coverage_mapping_result_json = self._create_completion(coverage_mapping_prompt, prompt_token_size)

        print("coverage mapping")

        logging.info("#################################################################")
        logging.info("#################################################################")
        logging.info("Coverage Mapping JSON Response: START")
        logging.info("#################################################################")
        logging.info("#################################################################")
        logging.info(coverage_mapping_result_json)
        logging.info("#################################################################")
        logging.info("#################################################################")
        logging.info("Coverage Mapping JSON Response: END")
        logging.info("#################################################################")
        logging.info("#################################################################")
        
        self.jsonUtils = JsonUtils(self.jira_issue)
        self.jsonUtils.json_writer(json_data=coverage_mapping_result_json, file_name="coverage_mapping")

        return coverage_mapping_result_json
    
    def sumarize_output(self) -> str:
        files = [
            "requirement_analysis", 
            "testcase_generation", 
            "risk_analysis", 
            "coverage_mapping"
            ]
        
        data = {}

        for file_name in files:
            self.jsonUtils = JsonUtils(self.jira_issue)
            data[file_name] = self.jsonUtils.json_reader(file_name=file_name)

        summarize_output_prompt, prompt_token_size = self.promptBuilder.build_summarize_output_prompt(data)
        summarize_output_result = self._create_completion(summarize_output_prompt, prompt_token_size)

        print("Summarize Output")

        logging.info("#################################################################")
        logging.info("#################################################################")
        logging.info("Summarize Output: START")
        logging.info("#################################################################")
        logging.info("#################################################################")
        logging.info(summarize_output_result)
        logging.info("#################################################################")
        logging.info("#################################################################")
        logging.info("Summarize Output: END")
        logging.info("#################################################################")
        logging.info("#################################################################")
        
        print(summarize_output_result)

        self.confluence_client = confluence_client.ConfluenceClient()
        
        page = self.confluence_client.create_or_update_page(
            space_key="QA",
            title=f"{self.jira_issue} - Automated QA Summary",
            body=summarize_output_result
        )

        # Extract URL from the response
        base_url = page.get("_links").get("base")
        url_endpoint = page.get("_links", "").get("webui") # where created page exists

        print("Success:", f"{base_url}{url_endpoint}")

        comment = f"Automated QA Summary has been generated and can be viewed at: {base_url}{url_endpoint}"

        self.jira_ticket = JiraClient()
        self.jira_ticket.add_comment_to_ticket(issue_key=self.jira_issue, comment=comment)

        return summarize_output_result
    

    # def test_confluence_connection(self):
        test_body = f"""
            ```html
            <h1>Story Overview</h1>

            <table>
                <tbody>
                    <tr>
                        <th>Story ID</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Story Summary</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Functional Intent</th>
                        <td></td>
                    </tr>
                </tbody>
            </table>

            <h1>Scope</h1>

            <h2>In Scope</h2>

            <ul>
                <li></li>
            </ul>

            <h2>Out of Scope</h2>

            <ul>
                <li></li>
            </ul>

            <h1>User Flows</h1>

            <ul>
                <li></li>
            </ul>

            <h1>Risk Areas</h1>

            <table>
                <thead>
                    <tr>
                        <th>Area</th>
                        <th>Severity</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                </tbody>
            </table>

            <h1>Acceptance Criteria</h1>

            <table>
                <thead>
                    <tr>
                        <th>AC ID</th>
                        <th>Description</th>
                        <th>Testable Points</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td></td>
                        <td></td>
                        <td>
                            <ul>
                                <li></li>
                            </ul>
                        </td>
                    </tr>
                </tbody>
            </table>

            <h1>Test Case Summary</h1>

            <table>
                <tbody>
                    <tr>
                        <th>Total Test Cases</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Positive Tests</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Negative Tests</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Security Tests</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Non-functional Tests</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Automation Candidates</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Manual Tests</th>
                        <td></td>
                    </tr>
                </tbody>
            </table>

            <h1>Generated Test Cases</h1>

            <table>
                <thead>
                    <tr>
                        <th>TC ID</th>
                        <th>Title</th>
                        <th>Category</th>
                        <th>Priority</th>
                        <th>Automation Candidate</th>
                        <th>Mapped AC</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                </tbody>
            </table>

            <h1>Risk Assessment</h1>

            <table>
                <thead>
                    <tr>
                        <th>TC ID</th>
                        <th>Overall Risk Score</th>
                        <th>Risk Level</th>
                        <th>Risk Rationale</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                </tbody>
            </table>

            <h1>Risk-Based Execution Order</h1>

            <ol>
                <li></li>
            </ol>

            <h1>Recommended Smoke Suite</h1>

            <ul>
                <li></li>
            </ul>

            <h1>Acceptance Criteria Coverage</h1>

            <table>
                <thead>
                    <tr>
                        <th>AC ID</th>
                        <th>Coverage Status</th>
                        <th>Covered By</th>
                        <th>Coverage Risk</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                </tbody>
            </table>

            <h1>Coverage Summary</h1>

            <table>
                <tbody>
                    <tr>
                        <th>Total Acceptance Criteria</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Fully Covered</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Partially Covered</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Not Covered</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Coverage Percentage</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Risk Weighted Coverage Percentage</th>
                        <td></td>
                    </tr>
                </tbody>
            </table>

            <h1>Coverage Gaps</h1>

            <table>
                <thead>
                    <tr>
                        <th>Gap Type</th>
                        <th>Description</th>
                        <th>Risk Level</th>
                        <th>Recommended Scenario</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                </tbody>
            </table>

            <h1>QA Recommendations</h1>

            <ul>
                <li></li>
            </ul>

            <h1>Executive Summary</h1>

            <p></p>
            ```

            """
    
        self.confluence_client = confluence_client.ConfluenceClient()
        page = self.confluence_client.create_or_update_page(
            space_key="QA",
            title="AQP-2 - Test Page",
            body=test_body
        )
        
        # Extract URL from the response
        print(page)

        url_endpoint = page.get("_links", "").get("webui")
        base_url = page.get("_links").get("base")

        print("Success:", f"{base_url}{url_endpoint}")

        comment = f"Automated QA Summary has been generated and can be viewed at: {base_url}{url_endpoint}"

        self.jira_ticket = JiraClient()
        self.jira_ticket.add_comment_to_ticket(issue_key=self.jira_issue, comment=comment)


        return test_body