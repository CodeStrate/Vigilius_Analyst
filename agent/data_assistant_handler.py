from agent.prompts import SMALL_TALK_PROMPT, INTENT_CLASSIFIER_PROMPT

class DataAssistant:
    def __init__(self, llm):
        self.assistant = llm

    def respond(self, user_input: str, current_intent: str = "small_talk", do_intent:bool = False) -> str:
        """
        Handle user interactions using Ollama local models
        
        Args:
            user_input: str = User's message
            current_intent: str = Current classified intent for context
            do_intent: bool = Whether to do intent classification or respond in small talk

        Returns:
            Intent classification or small talk / clarification response
        """
        try:
            messages = [{
                "role" : "system",
                "content" : INTENT_CLASSIFIER_PROMPT if do_intent else SMALL_TALK_PROMPT.format(intent=current_intent)
            },
            {
                "role" : "user",
                "content" : user_input
            }]
            
            response = self.assistant.invoke(messages)
            return response.content.strip()
        except Exception as e:
            # if intent fails fall to sql
            if do_intent:
                return "sql_query"
            else:
                return "I'm here to help with your data related queries. Could you please rephrase that?"

    def validate_intent(self, resp: str) -> str:
        """Validate LLM intent response for expected values"""

        valid_intents = ["sql_query", "small_talk", "clarification_needed"]
        for intent in valid_intents:
            if intent in resp.lower().strip():
                return intent
        
        return "small_talk"
