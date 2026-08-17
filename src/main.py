import logging
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from src.core.pipeline import QAStoryPipeline

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
    qa_story_pipeline_instance = QAStoryPipeline(jira_issue="AQP-2")
    qa_story_pipeline_instance.run()

if __name__ == "__main__":
    main()
