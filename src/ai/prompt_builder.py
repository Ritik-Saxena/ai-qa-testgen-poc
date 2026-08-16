import tiktoken

from src.atlassian.jira_parser import JiraParser

class PromptBuilder: 
	def build_requirement_prompt(self, issue_key):
		json_schema_requirement = {
			"story_id": "",
			"story_summary": "",
			"functional_intent": "",
			"in_scope_features": [],
			"out_of_scope_assumptions": [],
			"user_flows": [],
			"risk_areas": [
				{
				"area": "Security | Functional | Data | UX | Performance",
				"description": "",
				"severity": "Low | Medium | High | Critical"
				}
			],
			"acceptance_criteria_breakdown": [
				{
				"ac_id": "AC-1",
				"description": "",
				"testable_points": []
				}
			],
			"test_design_notes": ""
		}

		jira_parser_object = JiraParser()
		jira_ticket = jira_parser_object.jira_issue_json(issue_key)

		print("jira ticket json: ")
		print(jira_ticket)
		
		jira_ticket_requirement_prompt = f"""
		JSON SCHEMA (STRICT):
		{json_schema_requirement}

		You are a Senior QA Engineer with strong experience in requirement analysis and test design.
		Analyze the following Jira user story and perform a deep QA-oriented requirement breakdown.

		Your tasks:
		1. Restate instent
		2. List in & out of scope features assumptions
		3. Define E2E user flows
		4. Map key risks (functional, security, data, UX, performance) with severity
		5. Atomic breakdown of ACs into testable points
		6. Add QA design notes

		IMPORTANT:
		- No test cases or assumed requirements
		- Output MUST strictly follow the JSON schema provided.
		- Return ONLY valid JSON. No markdown, no explanations.

		Input:
		{jira_ticket}
		"""
		
		model_encode = tiktoken.encoding_for_model("gpt-oss-120b")
		prompt_tokens_size = len(model_encode.encode(jira_ticket_requirement_prompt))

		return jira_ticket_requirement_prompt, prompt_tokens_size
	
	def build_testcase_generate_prompt(self, requirement_analysis_json):
		json_schema_testcase = {
			"story_id": "",
			"test_cases": [
				{
				"test_case_id": "",
				"title": "",
				"category": "Positive | Negative | Edge | Security | NFR",
				"sub_category": "",
				"mapped_acceptance_criteria": ["AC-1"],
				"preconditions": [],
				"test_steps": [],
				"expected_result": "",
				"test_data": [],
				"priority": "P0 | P1 | P2",
				"automation_candidate": True,
				"automation_reason": ""
				}
			]
		}

		testcase_generate_prompt = f"""
			JSON SCHEMA (STRICT):
			{json_schema_testcase}

			You are a Senior SDET responsible for designing comprehensive test coverage.
			Using the requirement analysis JSON provided below, generate detailed test cases.

			Generate test cases covering:
			- Positive scenarios
			- Negative scenarios
			- Edge cases
			- Security scenarios
			- Non-functional scenarios (performance, accessibility, usability where applicable)

			For each test case:
			- Clearly map it to ACs
			- Ensure steps are concise but executable
			- Provide automation feasibility with reasoning

			IMPORTANT RULES:
			- Follow the provided JSON schema EXACTLY
			- Use realistic and professional test titles
			- Avoid redundant test cases
			- Return ONLY valid JSON. No markdown, no explanations

			Input:
			{requirement_analysis_json}
		"""

		model_encode = tiktoken.encoding_for_model("gpt-oss-120b")
		prompt_tokens_size = len(model_encode.encode(testcase_generate_prompt))


		return testcase_generate_prompt, prompt_tokens_size
	

	def build_risk_analysis_prioritization_prompt(self, generated_testcase_json):
		json_schema_risk_analysis = {
			"story_id": "",
			"risk_scoring_model": {
				"dimensions": [
				"business_impact",
				"user_impact",
				"failure_likelihood",
				"security_impact"
				],
				"score_range": "1-10",
				"scoring_notes": ""
			},
			"test_case_risk_scores": [
				{
				"test_case_id": "",
				"title": "",
				"category": "",
				"mapped_acceptance_criteria": ["AC-1"],
				"risk_scores": {
					"business_impact": 0,
					"user_impact": 0,
					"failure_likelihood": 0,
					"security_impact": 0
				},
				"overall_risk_score": 0.0,
				"risk_level": "Low | Medium | High | Critical",
				"risk_rationale": ""
				}
			],
			"prioritization_summary": {
				"execution_order": ["TC-06", "TC-03", "TC-01"],
				"high_risk_tests": ["TC-06"],
				"recommended_smoke_suite": ["TC-01", "TC-06"]
			}
		}

		risk_analysis_prompt = f"""
			JSON SCHEMA (STRICT):
			{json_schema_risk_analysis}

			You are a QA Lead responsible for risk-based test prioritization.
			Using the structured test cases provided below, evaluate the risk of each test case.

			Risk scoring rules:
			- Score each dimension on a scale of 1 to 10; 10 is highest risk/impact
			- Overall risk score should be a calculated average of all dimensions
			- Assign a risk level based on overall score:
			- 1–3   → Low
			- 4–6   → Medium
			- 7–8   → High
			- 9–10  → Critical

			Risk dimensions to evaluate:
			- Business Impact: Impact on business or compliance if this fails in production
			- User Impact: Severity of impact on end users
			- Failure Likelihood: Probability of this scenario failing in real usage
			- Security Impact: Potential security or data exposure risk

			IMPORTANT:
			- Output MUST strictly follow the JSON schema provided.
			- Return ONLY valid JSON. No markdown, no explanations

			Input Test Cases:
			{generated_testcase_json}
		"""

		model_encode = tiktoken.encoding_for_model("gpt-oss-120b")
		prompt_tokens_size = len(model_encode.encode(risk_analysis_prompt))


		return risk_analysis_prompt, prompt_tokens_size
	
	def build_coverage_mapping_gap_detection_prompt(self, acceptance_criteria, generated_testcase_json, risk_analysis_json):
		json_schema_coverage_gap = {
			"story_id": "",
			"acceptance_criteria_coverage": [
				{
				"ac_id": "AC-1",
				"ac_description": "",
				"covered_by_test_cases": [],
				"coverage_status": "Covered | Partially Covered | Not Covered",
				"coverage_risk": "Low | Medium | High | Critical"
				}
			],
			"coverage_summary": {
				"total_acceptance_criteria": 0,
				"fully_covered": 0,
				"partially_covered": 0,
				"not_covered": 0,
				"coverage_percentage": 0,
				"risk_weighted_coverage_percentage": 0
			},
			"identified_coverage_gaps": [
				{
				"gap_type": "Missing Scenario | Weak Coverage | Missing NFR | Missing Security",
				"description": "",
				"affected_acceptance_criteria": [],
				"risk_level": "Low | Medium | High | Critical",
				"recommended_test_scenario": ""
				}
			],
			"qa_recommendations": []
			}

		coverage_mapping_prompt = f"""
			JSON SCHEMA (STRICT):
			{json_schema_coverage_gap}

			You are a QA Architect responsible for validating test coverage quality.

			Using the following inputs:
			1. Acceptance criteria breakdown
			2. Generated test cases
			3. Risk scoring results

			Perform a coverage analysis with the goals below.

			YOUR TASKS:
			1. Map each acceptance criterion to the test cases that validate it.
			2. Mark coverage status as:
			- Covered (adequate test coverage)
			- Partially Covered (basic coverage but missing important scenarios)
			- Not Covered (no meaningful test coverage)
			3. Assign coverage risk based on:
			- Business criticality
			- Security impact
			- Risk scores of related test cases
			4. Calculate:
			- Overall coverage percentage
			- Risk-weighted coverage percentage
			5. Identify coverage gaps, including:
			- Missing security scenarios
			- Missing edge cases
			- Missing non-functional scenarios
			6. Recommend additional test scenarios to close high-risk gaps.
			7. Provide concise QA recommendations.

			IMPORTANT RULES:
			- Return ONLY valid JSON. No markdown, no explanations
			- Base analysis strictly on the provided inputs.

			INPUT DATA:
			Acceptance Criteria:
			{acceptance_criteria}
			Test Cases:
			{generated_testcase_json}
			Risk Scoring:
			{risk_analysis_json}
		"""

		model_encode = tiktoken.encoding_for_model("gpt-oss-120b")
		prompt_tokens_size = len(model_encode.encode(coverage_mapping_prompt))


		return coverage_mapping_prompt, prompt_tokens_size
	
	def build_summarize_output_prompt(self, data):
		summarize_output_prompt = f"""
			You are an experienced QA Lead responsible for generating a professional Confluence report for a Jira Story.

			You will receive the outputs from the following AI QA pipeline:

			1. Requirement Analysis
			{data["requirement_analysis"]}
			2. Test Case Generation
			{data["testcase_generation"]}
			3. Risk Analysis
			{data["risk_analysis"]}
			4. Coverage Mapping
			{data["coverage_mapping"]}

			Your responsibility is to consolidate all of these outputs into a single, well-structured Confluence document.

			Do NOT invent any information.
			Do NOT create new test cases.
			Do NOT modify any risk scores.
			Do NOT change any acceptance criteria.
			Only summarize, organize, and present the provided information in a clean and readable Confluence format.

			Generate the final report in Confluence Storage Format (HTML).

				Use:

				H1: Story Overview
				- Table: Story ID, Story Summary, Functional Intent

				H1: Scope
				- H2: In Scope (unordered list)
				- H2: Out of Scope (unordered list)

				H1: User Flows
				- Unordered list

				H1: Risk Areas
				- Table: Area | Severity | Description

				H1: Acceptance Criteria
				- Table: AC ID | Description | Testable Points

				H1: Test Case Summary
				- Two-column table

				H1: Generated Test Cases
				- Table: TC ID | Title | Category | Priority | Automation Candidate | Mapped AC

				H1: Risk Assessment
				- Table: TC ID | Overall Risk Score | Risk Level | Risk Rationale

				H1: Risk-Based Execution Order
				- Ordered list

				H1: Recommended Smoke Suite
				- Unordered list

				H1: Acceptance Criteria Coverage
				- Table: AC ID | Coverage Status | Covered By | Coverage Risk

				H1: Coverage Summary
				- Two-column table

				H1: Coverage Gaps
				- Table: Gap Type | Description | Risk Level | Recommended Scenario

				H1: QA Recommendations
				- Unordered list

				H1: Executive Summary
				- Paragraph (maximum 200 words)

				Return only valid Confluence Storage Format (HTML).

			The executive summary should only be based on the provided inputs.

			Do not make assumptions.

			Output only the final Confluence report.

			Do not output JSON.
			Do not explain your reasoning.
			Do not mention the pipeline steps.
			"""
		
		model_encode = tiktoken.encoding_for_model("gpt-oss-120b")
		prompt_tokens_size = len(model_encode.encode(summarize_output_prompt))

		return summarize_output_prompt, prompt_tokens_size
