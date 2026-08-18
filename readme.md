# AI-Powered QA Test Generation PoC

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

## 📋 Description

**AI QA Test Generation PoC** is an intelligent test automation framework that answers the critical question: 
> **Can AI generate test scenarios from user stories, identify coverage gaps, assess risk, and suggest automation readiness to reduce QA manual effort?**

This proof-of-concept integrates with Atlassian JIRA and Confluence to automatically analyze user stories and generate comprehensive QA artifacts using advanced LLM capabilities (powered by Groq).

### Core Value Propositions

- ✅ **Requirement Analysis** - Deep breakdown of requirements with edge cases and acceptance criteria
- ✅ **Automated Test Case Generation** - Generate test scenarios directly from JIRA user stories
- ✅ **Risk Assessment** - Intelligent risk prioritization based on test coverage
- ✅ **Coverage Mapping** - Identify test coverage gaps and automation readiness
- ✅ **Confluence Integration** - Automated documentation and reporting to Confluence

---

## 📑 Table of Contents

- [Getting Started](#getting-started)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage--running-the-project)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [System Workflow](#system-workflow)
- [Technology Stack](#technology-stack)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

---
<a id="getting-started"></a>
## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following:

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Git** - For cloning the repository
- **pip** - Python package manager (comes with Python)

### External Service Accounts (Required)

1. **Atlassian Account**
   - JIRA instance URL (e.g., `https://yourcompany.atlassian.net`)
   - Email associated with your Atlassian account
   - API Token - [Generate API Token](https://id.atlassian.com/manage-profile/security/api-tokens)
   - Confluence API access for documentation publishing

2. **Groq API Key**
   - Sign up at [Groq Console](https://console.groq.com)
   - Create an API key for LLM access
   - Verify API quota is sufficient

<a id="installation"></a>
### Installation

1. **Clone the repository**
   ```bash
   https://github.com/Ritik-Saxena/ai-qa-testgen-poc.git
   cd ai-qa-testgen-poc
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

<a id="configuration"></a>
### Configuration

1. **Create `.env` file from template**
   ```bash
   cp .env.example .env
   ```

2. **Update `.env` with your credentials**
   ```env
   # Atlassian Configuration
   Atlassian_BASE_URL=https://your-company.atlassian.net
   Atlassian_EMAIL=your-email@company.com
   Atlassian_API_TOKEN=your-atlassian-api-token
   Atlassian_CLOUD=true

   # Groq LLM Configuration
   GROQ_API_KEY=your-groq-api-key
   LLM_MODEL=openai/gpt-oss-120b
   MAX_TOKENS=8000
   ```

**Environment Variables Reference:**

| Variable | Description | Example |
|----------|-------------|---------|
| `Atlassian_BASE_URL` | Your JIRA instance URL | `https://company.atlassian.net` |
| `Atlassian_EMAIL` | Email for JIRA API authentication | `user@company.com` |
| `Atlassian_API_TOKEN` | JIRA API token for authentication | Generated from Atlassian profile |
| `Atlassian_CLOUD` | Use Atlassian Cloud (true/false) | `true` |
| `GROQ_API_KEY` | API key for Groq LLM service | Generated from Groq console |
| `LLM_MODEL` | LLM model to use | `openai/gpt-oss-120b` |
| `MAX_TOKENS` | Maximum token limit per request | `8000` |

**Reference Links:**
- [Atlassian Basic Auth REST APIs](https://developer.atlassian.com/cloud/confluence/basic-auth-for-rest-apis/)
- [Generate Atlassian API Token](https://id.atlassian.com/manage-profile/security/api-tokens)

---

<a id="usage--running-the-project"></a>
## 💻 Usage & Running the Project

### Run the Pipeline

To execute the QA workflow on a specific JIRA issue:

```bash
python -m src.main
```

The pipeline will process the issue and generate outputs. To change the JIRA issue key, modify [src/main.py](src/main.py):

```python
def main():
    qa_story_pipeline_instance = QAStoryPipeline(jira_issue="YOUR-ISSUE-KEY")
    qa_story_pipeline_instance.run()
```

### What the Pipeline Does

The workflow executes 5 sequential steps:

```
User Story (JIRA) 
       ↓
1️⃣  Requirement Analysis → requirement_analysis.json
       ↓
2️⃣  Test Case Generation → testcase_generation.json
       ↓
3️⃣  Risk Analysis & Prioritization → risk_analysis.json
       ↓
4️⃣  Coverage Mapping → coverage_mapping.json
       ↓
5️⃣  Summary & Confluence Documentation
```

### Output Files

Generated artifacts are saved to `output/{JIRA_ISSUE_KEY}/`:

- **requirement_analysis.json** - Detailed requirement breakdown with edge cases
- **testcase_generation.json** - Auto-generated test scenarios and test cases
- **risk_analysis.json** - Risk assessment and test prioritization
- **coverage_mapping.json** - Test coverage analysis and gaps
- **Confluence Page** - Published documentation summary

### Logs

Application logs are saved to `logs/` directory with timestamp:
```
logs/ai_qa_poc_2024-01-15_10-30-45.log
```

---
<a id="architecture"></a>
## 🏗️ Architecture

### System Architecture

<img width="5688" height="1612" alt="architectural diagram" src="https://github.com/user-attachments/assets/7e8f735c-a7f2-422a-a97f-566751ce87d5" />


### Data Flow

```
1. JIRA Issue Retrieved → Parsed & Normalized
                    ↓
2. Requirement Prompt Built → Sent to Groq LLM
                    ↓
3. Requirement Analysis JSON Generated
                    ↓
4. Test Case Prompt Built → Sent to Groq LLM
                    ↓
5. Test Case Generation JSON Generated
                    ↓
6. Risk Analysis Prompt Built → Sent to Groq LLM
                    ↓
7. Risk Analysis JSON Generated
                    ↓
8. Coverage Mapping Prompt Built → Sent to Groq LLM
                    ↓
9. Coverage Mapping JSON Generated
                    ↓
10. Summary Generated & Published to Confluence
```

<img width="6034" height="676" alt="Data flow diagram" src="https://github.com/user-attachments/assets/be3913ec-a2b5-478b-908a-ae3112b88967" />

### Component Responsibilities

```
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
```

| Component | Responsibility |
|-----------|-----------------|
| **QAStoryPipeline** | Orchestrates entire workflow, coordinates 5 pipeline steps |
| **QAWorkflowService** | Implements core business logic for each workflow step |
| **PromptBuilder** | Constructs AI prompts and counts tokens |
| **LLMClient** | Interfaces with Groq API for LLM completions |
| **JiraClient** | Retrieves and manages JIRA issues |
| **ConfluenceService** | Publishes results to Confluence pages |
| **WorkflowState** | State container passing data between pipeline steps |
| **JsonUtils** | Handles JSON output and file writing |
| **JiraParser** | Parses JIRA responses into structured data |
| **LogUtils** | Handles application logging |

---

<a id="project-structure"></a>
## 📁 Project Structure

```
ai-qa-testgen-poc/
│
├── README.md                          # Project documentation (this file)
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
│
├── config/                            # Configuration module
│   ├── __init__.py
│   └── settings.py                    # App settings & environment validation
│
├── src/                               # Main source code
│   ├── __init__.py
│   ├── main.py                        # Entry point for the application
│   │
│   ├── core/                          # Core pipeline orchestration
│   │   ├── __init__.py
│   │   └── pipeline.py                # QAStoryPipeline class
│   │
│   ├── ai/                            # AI & LLM integration
│   │   ├── __init__.py
│   │   └── prompts/
│   │       ├── __init__.py
│   │       └── builder.py             # Prompt construction & token counting
│   │
│   ├── clients/                       # External service clients
│   │   ├── __init__.py
│   │   ├── atlassian/
│   │   │   ├── __init__.py
│   │   │   ├── jira_client.py         # JIRA API wrapper
│   │   │   └── confluence_client.py   # Confluence API wrapper
│   │   └── llm/
│   │       ├── __init__.py
│   │       └── llm_client.py          # Groq LLM API client
│   │
│   ├── parsers/                       # Data parsing & transformation
│   │   ├── __init__.py
│   │   └── jira_parser.py             # JIRA issue parser
│   │
│   ├── services/                      # Business logic & orchestration
│   │   ├── __init__.py
│   │   ├── qa_workflow_service.py     # Core QA workflow logic
│   │   └── confluence_service.py      # Confluence integration
│   │
│   └── utils/                         # Utility functions
│       ├── __init__.py
│       ├── json_utils.py              # JSON I/O operations
│       └── log_utils.py               # Logging utilities
│
├── logs/                              # Application logs
│   └── ai_qa_poc_YYYY-MM-DD_HH-MM-SS.log
│
└── output/                            # Generated QA artifacts
    └── {JIRA_ISSUE_KEY}/              # Folder per JIRA issue
        ├── requirement_analysis.json
        ├── testcase_generation.json
        ├── risk_analysis.json
        └── coverage_mapping.json
```

---
<a id="system-workflow"></a>
## 🔄 System Workflow

### Step 1: Requirement Analysis
- **Input:** JIRA user story/issue
- **Output:** Detailed requirement breakdown with:
  - Functional requirements
  - Non-functional requirements
  - Edge cases and boundary conditions
  - Acceptance criteria
  - Assumptions and dependencies

### Step 2: Test Case Generation
- **Input:** Requirement analysis JSON
- **Output:** Test scenarios with:
  - Test case descriptions
  - Prerequisites and setup steps
  - Test steps and expected results
  - Data requirements
  - Positive/negative test cases

### Step 3: Risk Analysis & Prioritization
- **Input:** Test case generation JSON
- **Output:** Risk assessment including:
  - Risk levels (High, Medium, Low)
  - Affected components
  - Test case prioritization
  - Coverage analysis
  - Automation readiness score

### Step 4: Coverage Mapping
- **Input:** Risk analysis JSON
- **Output:** Coverage matrix with:
  - Requirement-to-test mapping
  - Coverage gaps
  - Manual vs. Automated test recommendations
  - Test execution strategy

### Step 5: Documentation & Publishing
- **Input:** All previous outputs
- **Output:** 
  - Summary report
  - Confluence page publication
  - HTML/PDF documentation (if configured)

---
<a id="technology-stack"></a>
## 📊 Technology Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.8+ |
| **LLM Service** | Groq (OpenAI-compatible) |
| **Project Management** | JIRA Cloud API |
| **Documentation** | Confluence API |
| **Token Counting** | TikToken |
| **API Client** | Requests |
| **Environment Management** | python-dotenv |

### Dependencies

```
groq==1.6.0
jira==3.10.5
python-dotenv==1.2.2
requests==2.34.2
tiktoken==0.12.0
```

---
<a id="api-reference"></a>
## 🔧 API Reference

### Main Entry Point

**File:** `src/main.py`

```python
from src.core.pipeline import QAStoryPipeline

# Run the pipeline for a specific JIRA issue
pipeline = QAStoryPipeline(jira_issue="AQP-2")
pipeline.run()
```

### Core Classes

#### QAStoryPipeline
Orchestrates the complete workflow.

```python
qa_pipeline = QAStoryPipeline(jira_issue="YOUR-ISSUE-KEY")
qa_pipeline.run()  # Executes all 5 steps
```

#### QAWorkflowService
Implements individual workflow steps.

```python
service = QAWorkflowService(jira_issue="YOUR-ISSUE-KEY")
state = WorkflowState("YOUR-ISSUE-KEY")

service.get_requirement_breakdown(state)    # Step 1
service.get_testcase_generation(state)      # Step 2
service.get_risk_analysis(state)            # Step 3
service.get_coverage_mapping(state)         # Step 4
service.sumarize_output(state)              # Step 5
```

#### LLMClient
Interfaces with Groq LLM API.

```python
from src.clients.llm.llm_client import LLMClient

llm = LLMClient(jira_issue="YOUR-ISSUE-KEY")
response = llm._create_completion(prompt, token_size)
```


---
<a id="troubleshooting"></a>
## 🆘 Troubleshooting

### Common Issues

**Issue:** `RuntimeError: LLM_MODEL environment variable is not set`
- **Solution:** Ensure `.env` file is created and `LLM_MODEL` is set correctly

**Issue:** `JIRA Authentication Error`
- **Solution:** Verify Atlassian API token and email are correct in `.env`

**Issue:** `Groq API Error`
- **Solution:** Check GROQ_API_KEY is valid and has sufficient quota

**Issue:** `ModuleNotFoundError: No module named 'src'`
- **Solution:** Ensure you're running from the project root directory and dependencies are installed

**Issue:** `Connection timeout to Atlassian/Groq`
- **Solution:** Check internet connectivity and verify API endpoints are accessible

### Logging

Enable debug logging by modifying `config/settings.py` or environment variables. Logs are saved to `logs/` directory for troubleshooting.

---

If you like this repository, do <img src="https://user-images.githubusercontent.com/62079355/200077014-f3e95bba-57a6-4c7a-b26a-212bf18e5162.png" width=25 height=25> and <img src="https://user-images.githubusercontent.com/62079355/220893415-ea2015e9-6df6-4de2-ab66-041a3f890be2.png" width=25 height=25> the repo for more amazing stuff coming soon.

---
[![GitHub stars](https://img.shields.io/github/stars/Ritik-Saxena/ai-qa-testgen-poc?style=social)](https://github.com/Ritik-Saxena/ai-qa-testgen-poc)
[![GitHub followers](https://img.shields.io/github/followers/Ritik-Saxena?style=social)](https://github.com/Ritik-Saxena?tab=followers)
[![GitHub forks](https://img.shields.io/github/forks/Ritik-Saxena/ai-qa-testgen-poc?style=social)](https://github.com/Ritik-Saxena/ai-qa-testgen-poc)
[![GitHub watchers](https://img.shields.io/github/watchers/Ritik-Saxena/ai-qa-testgen-poc?style=social)](https://github.com/Ritik-Saxena/ai-qa-testgen-poc)

