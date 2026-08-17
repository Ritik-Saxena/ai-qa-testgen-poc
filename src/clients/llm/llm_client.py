from groq import Groq
from config import settings
from src.ai.prompts.builder import PromptBuilder
from src.utils.log_utils import log_info

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

        log_info(f"Prompt Token Size: {prompt_token_size}")
        log_info(f"Final Token Size: {final_token_size}")
        
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
