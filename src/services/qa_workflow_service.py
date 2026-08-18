import json

from src.ai.prompts.builder import PromptBuilder
from src.utils.json_utils import JsonUtils
from src.services.confluence_service import ConfluenceService
from src.clients.atlassian.jira_client import JiraClient
from src.clients.llm.llm_client import LLMClient
from src.utils.log_utils import log_response 

class WorkflowState:
    def __init__(self, jira_issue):
        self.jira_issue = jira_issue
        self.requirement_analysis_json = None
        self.testcase_generation_json = None
        self.risk_analysis_json = None
        self.coverage_mapping_json = None
        self.summary = None
        self.status = "initialized"
        self.error = []

class QAWorkflowService:
    def __init__(self, jira_issue):
        self.jira_issue = jira_issue
        self.promptBuilder = PromptBuilder(jira_issue)
        self.jsonUtils = JsonUtils(jira_issue)
        self.llm_client = LLMClient(jira_issue)
        self.confluence_service = ConfluenceService()
        
    def get_requirement_breakdown(self, state: WorkflowState):
            try:
                requirement_prompt, prompt_token_size = self.promptBuilder.build_requirement_prompt(self.jira_issue)    # build_requirement_prompt returns [requirement_prompt, prompt_tokens_size]
                state.requirement_analysis_json = self.llm_client._create_completion(requirement_prompt, prompt_token_size)

                print("requirements breakdown")
                log_response("Requirement Analysis JSON Response", state.requirement_analysis_json)
                
                self.jsonUtils = JsonUtils(self.jira_issue)
                self.jsonUtils.json_writer(json_data=state.requirement_analysis_json, file_name="requirement_analysis")

            except Exception as e:
                state.error.append(f"Requirement breakdown failed: {e}")
                state.status = "failed"
                raise



    def get_testcase_generation(self, state: WorkflowState):
        try:
            generate_testcase_prompt, prompt_token_size = self.promptBuilder.build_testcase_generate_prompt(state.requirement_analysis_json)
            
            state.testcase_generation_json = self.llm_client._create_completion(generate_testcase_prompt, prompt_token_size)

            print("test case generation")

            log_response("Test Case Generation JSON Response", state.testcase_generation_json)
            
            self.jsonUtils = JsonUtils(self.jira_issue)
            self.jsonUtils.json_writer(json_data=state.testcase_generation_json, file_name="testcase_generation")

        except Exception as e:
            state.error.append(f"Testcase generation failed: {e}")
            state.status = "failed"
            raise
    
    
    def get_risk_analysis(self, state: WorkflowState):
        try:
            risk_analysis_prompt, prompt_token_size = self.promptBuilder.build_risk_analysis_prioritization_prompt(state.testcase_generation_json)

            state.risk_analysis_json = self.llm_client._create_completion(risk_analysis_prompt, prompt_token_size)
        
            print("risk analysis")

            log_response("Risk Analysis JSON Response", state.risk_analysis_json)
            
            self.jsonUtils = JsonUtils(self.jira_issue)
            self.jsonUtils.json_writer(json_data=state.risk_analysis_json, file_name="risk_analysis")

        except Exception as e:
                state.error.append(f"Risk analysis failed: {e}")
                state.status = "failed"
                raise

    def get_coverage_mapping(self, state: WorkflowState):
        try:
            requirement_data = json.loads(state.requirement_analysis_json)
            acceptance_criteria = requirement_data.get("acceptance_criteria_breakdown", [])
            testcase_generation_json = state.testcase_generation_json
            risk_analysis_json = state.risk_analysis_json
            
            coverage_mapping_prompt, prompt_token_size = self.promptBuilder.build_coverage_mapping_gap_detection_prompt(
                                                            acceptance_criteria, 
                                                            testcase_generation_json, 
                                                            risk_analysis_json
                                                            )

            state.coverage_mapping_json = self.llm_client._create_completion(coverage_mapping_prompt, prompt_token_size)

            print("coverage mapping")

            log_response("Coverage Mapping JSON Response", state.coverage_mapping_json)
            
            self.jsonUtils = JsonUtils(self.jira_issue)
            self.jsonUtils.json_writer(json_data=state.coverage_mapping_json, file_name="coverage_mapping")

        except Exception as e:
            state.error.append(f"Coverage mapping failed: {e}")
            state.status = "failed"
            raise
            
    
    def sumarize_output(self, state: WorkflowState) -> str:
        try:
            data = {
                "requirement_analysis": state.requirement_analysis_json,
                "testcase_generation": state.testcase_generation_json,
                "risk_analysis": state.risk_analysis_json,
                "coverage_mapping": state.coverage_mapping_json
            }

            summarize_output_prompt, prompt_token_size = self.promptBuilder.build_summarize_output_prompt(data)
            summarize_output_result = self.llm_client._create_completion(summarize_output_prompt, prompt_token_size)

            print("Summarize Output")

            log_response("Summarize Output", summarize_output_result)

            # Creating the confluence page for the AI generated summary for the Jira story            
            page = self.confluence_service.create_or_update_page(
                space_key="QA",
                title=f"{self.jira_issue} - Automated QA Summary",
                body=summarize_output_result
            )

            # Extract URL from the response
            base_url = page.get("_links").get("base")
            url_endpoint = page.get("_links", "").get("webui") # where created page exists

            print("Success:", f"{base_url}{url_endpoint}")

            # Adding comment to the Jira ticket with the URL of generated confluence page
            comment = f"Automated QA Summary has been generated and can be viewed at: {base_url}{url_endpoint}"

            self.jira_ticket = JiraClient()
            self.jira_ticket.add_comment_to_ticket(issue_key=self.jira_issue, comment=comment)

        except Exception as e:
                state.error.append(f"Summarize output failed: {e}")
                state.status = "failed"
                raise
