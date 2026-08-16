import logging
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from src.ai.llm_client import LLMClient

# Loading environment variables from .env file
load_dotenv()

# Adjusting sys.path to ensure imports work correctly regardless of execution context
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) in sys.path:
    sys.path.remove(str(SRC_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# Logs
datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"logs/ai_qa_poc_{datetime_str}.log"

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)



def main():

    llm_client_instance = LLMClient(jira_issue="AQP-2")
    # llm_client_instance.get_requirement_breakdown()
    # llm_client_instance.get_testcase_generation()
    # llm_client_instance.get_risk_analysis()
    llm_client_instance.get_coverage_mapping()

    llm_client_instance.sumarize_output()
    # llm_client_instance.test_confluence_connection()


if __name__ == "__main__":
    main()
    
