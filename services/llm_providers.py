from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging
from core.config import get_settings
import google.generativeai as genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.settings = get_settings()
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        """Generate text using the LLM"""
        pass

class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        try:
            # In a real implementation, use the Anthropic client
            # import anthropic
            # client = anthropic.AsyncAnthropic(api_key=self.settings.ANTHROPIC_API_KEY)
            
            # Simulate Claude response for demo
            logger.info(f"Claude ({self.model_name}) generating response")
            return f"[{self.model_name}] Simulated response to: {prompt[:100]}..."
            
        except Exception as e:
            logger.error(f"Error generating Claude response: {e}")
            raise

class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        try:
            # In a real implementation, use the OpenAI client
            # from openai import AsyncOpenAI
            # client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
            
            # Simulate OpenAI response for demo
            logger.info(f"OpenAI ({self.model_name}) generating response")
            return f"[{self.model_name}] Simulated response to: {prompt[:100]}..."
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            raise

class GeminiProvider(LLMProvider):
    """Google Gemini provider"""

    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        if not self.settings.GOOGLE_API_KEY:
            logger.error("GOOGLE_API_KEY not configured.")
            raise ValueError("GOOGLE_API_KEY is not set in the environment or configuration.")

        try:
            genai.configure(api_key=self.settings.GOOGLE_API_KEY)
            
            model_init_kwargs = {}
            if system_prompt:
                # For Gemini, system instructions are typically passed during model initialization
                model_init_kwargs['system_instruction'] = system_prompt
            
            # model_name should be like "gemini-1.5-flash", "gemini-pro", etc.
            model = genai.GenerativeModel(self.model_name, **model_init_kwargs)
            
            logger.info(f"Gemini ({self.model_name}) generating response for prompt: {prompt[:100]}...")
            
            # Only include tools for search/research tasks, not for report generation
            use_tools = kwargs.get('use_tools', True)
            tools = None
            
            if use_tools and not any(keyword in prompt.lower() for keyword in ['generate a comprehensive intelligence report', 'parse the json response', 'analysis based on all collected data']):
                # Configure the Google Search tool for research tasks
                tools = [{
                    "function_declarations": [{
                        "name": "google_search",
                        "description": "Search Google for real-time information",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "query": {
                                    "type": "STRING",
                                    "description": "The search query"
                                }
                            },
                            "required": ["query"]
                        }
                    }]
                }]

            response = await model.generate_content_async(prompt, tools=tools)
            
            full_response_text = ""
            # Iterating through candidates and parts is a robust way to get all text
            # especially if there are multiple candidates or parts.
            if response.candidates:
                for candidate in response.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'text'):
                                full_response_text += part.text
            
            if not full_response_text:
                # Check for blockages or other issues if no text was extracted
                if response.prompt_feedback:
                    logger.warning(
                        f"Prompt Feedback for {self.model_name}: Block Reason: {response.prompt_feedback.block_reason}, "
                        f"Message: {response.prompt_feedback.block_reason_message}"
                    )
                    return f"[{self.model_name}] Could not generate a response. The prompt may have been blocked or resulted in no content due to safety settings. Details: {response.prompt_feedback.block_reason}"
                # .text can raise an error if the response was blocked or had no content.
                try:
                    # This is a simpler way if you expect a single text response and no blocking.
                    # However, it's less robust than iterating through candidates and parts.
                    full_response_text = response.text 
                except ValueError as ve:
                    logger.warning(f"Gemini response issue for {self.model_name} (ValueError accessing .text): {ve}. Prompt: {prompt[:100]}...")
                    return f"[{self.model_name}] Could not generate a response. The prompt may have been blocked or resulted in empty content."

            if not full_response_text:
                 logger.warning(f"Gemini ({self.model_name}) returned an empty response or a response without text parts. Prompt: {prompt[:100]}...")
                 return f"[{self.model_name}] Received an empty response from the model."


            logger.info(f"Gemini ({self.model_name}) generated response successfully.")
            return full_response_text
            
        except Exception as e:
            # Log the full exception details for debugging
            logger.error(f"Error generating Gemini response for {self.model_name} with prompt '{prompt[:100]}...': {e}", exc_info=True)
            # You might want to catch specific exceptions from the google.generativeai library
            # e.g., google.api_core.exceptions.PermissionDenied for API key issues
            # or google.api_core.exceptions.InvalidArgument for model name issues.
            raise # Re-raise the exception to be handled by the caller

def get_llm_provider(model_name: str) -> LLMProvider:
    """Factory function to get appropriate LLM provider"""
    model_name_lower = model_name.lower()
    if "claude" in model_name_lower:
        return ClaudeProvider(model_name)
    elif "gpt" in model_name_lower:
        return OpenAIProvider(model_name)
    elif "gemini" in model_name_lower:
        return GeminiProvider(model_name)
    else:
        raise ValueError(f"Unsupported model: {model_name}")
