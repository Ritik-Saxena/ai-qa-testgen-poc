from src.services.qa_workflow_service import QAWorkflowService, WorkflowState

class QAStoryPipeline:
    def __init__(self, jira_issue):
        self.jira_issue = jira_issue
        self.qa_workflow_service = QAWorkflowService(self.jira_issue)

    def run(self):
        state = WorkflowState(self.jira_issue)

        # 1. Generating the requirement for the ticket
        self.qa_workflow_service.get_requirement_breakdown(state)

        # 2. Generate testcase using requirement analysis output JSON
        self.qa_workflow_service.get_testcase_generation(state)
        
        # 3. Generate the risk analysis using testcase output JSON
        self.qa_workflow_service.get_risk_analysis(state)

        # 4. Generate the coverage mapping for the Jira issue
        self.qa_workflow_service.get_coverage_mapping(state)

        # 5. Generate the summary & create the confluence page for the ticket
        self.qa_workflow_service.sumarize_output(state)
