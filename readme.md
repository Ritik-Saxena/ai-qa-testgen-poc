Main Question:

Can AI generate test scenarios from user stories, identify coverage gaps, assess risk, and suggest automation readiness to reduce QA manual effort?


Atlassian Basic Auth Rest APIs doc:
https://developer.atlassian.com/cloud/confluence/basic-auth-for-rest-apis/


Atlassian API Token:
https://id.atlassian.com/manage-profile/security/api-tokens


                 QAWorkflowService
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    PromptBuilder    LLMClient       JsonUtils
          │              │              │
          └──────────────┼──────────────┘
                         │
                         ▼
                  WorkflowState
