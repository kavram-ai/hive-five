"""
GLM-4.6 LLM Client with retry logic and error handling

Integrates with Zhipu AI's GLM-4 API for agent reasoning and response generation.
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import aiohttp
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LLMRequest(BaseModel):
    """Request to LLM"""
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=4096)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)


class LLMResponse(BaseModel):
    """Response from LLM"""
    content: str
    finish_reason: str
    usage: Dict[str, Any]  # Changed from Dict[str, int] to support nested structures
    latency_ms: float


class GLMClient:
    """
    Client for GLM-4.6 API with automatic retry and error handling

    Features:
    - Exponential backoff retry logic
    - Token usage tracking
    - Latency monitoring
    - Error handling with fallback responses
    """

    def __init__(
        self,
        api_key: str,
        api_url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        model: str = "glm-4-flash",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize GLM client

        Args:
            api_key: Zhipu AI API key
            api_url: API endpoint URL
            model: Model name (glm-4-flash, glm-4, etc.)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

        self.session: Optional[aiohttp.ClientSession] = None

        # Metrics
        self.total_requests = 0
        self.total_tokens = 0
        self.total_errors = 0

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def start(self):
        """Initialize HTTP session"""
        if self.session is None:
            timeout_obj = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout_obj)
            logger.info(f"GLM client started with model: {self.model}")

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("GLM client closed")

    async def generate(self, request: LLMRequest) -> Optional[LLMResponse]:
        """
        Generate response from LLM with retry logic

        Args:
            request: LLM request configuration

        Returns:
            LLM response or None if all retries failed
        """
        if not self.session:
            await self.start()

        for attempt in range(self.max_retries):
            try:
                response = await self._make_request(request)
                self.total_requests += 1
                return response

            except asyncio.TimeoutError:
                logger.warning(f"LLM request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    self.total_errors += 1
                    return None
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

            except aiohttp.ClientError as e:
                logger.error(f"LLM request failed: {e} (attempt {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    self.total_errors += 1
                    return None
                await asyncio.sleep(2 ** attempt)

            except Exception as e:
                logger.error(f"Unexpected error in LLM request: {e}")
                self.total_errors += 1
                return None

        return None

    async def _make_request(self, request: LLMRequest) -> LLMResponse:
        """
        Make actual API request to GLM

        Args:
            request: LLM request configuration

        Returns:
            LLM response

        Raises:
            aiohttp.ClientError: On HTTP errors
            asyncio.TimeoutError: On timeout
        """
        start_time = datetime.utcnow()

        # Build messages
        messages = []
        if request.system_prompt:
            messages.append({
                "role": "system",
                "content": request.system_prompt
            })

        messages.append({
            "role": "user",
            "content": request.prompt
        })

        # Build request payload
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/kavram-ai/hive-five",  # Required by OpenRouter
            "X-Title": "Hive Five Multi-Agent System"  # Optional but recommended
        }

        # Make request
        async with self.session.post(
            self.api_url,
            json=payload,
            headers=headers
        ) as response:
            response.raise_for_status()
            data = await response.json()

        # Calculate latency
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Parse response
        choice = data["choices"][0]
        content = choice["message"]["content"]
        finish_reason = choice["finish_reason"]
        usage = data.get("usage", {})

        # Track token usage
        total_tokens = usage.get("total_tokens", 0)
        self.total_tokens += total_tokens

        logger.debug(
            f"LLM response received: {len(content)} chars, "
            f"{total_tokens} tokens, {latency_ms:.0f}ms"
        )

        return LLMResponse(
            content=content,
            finish_reason=finish_reason,
            usage=usage,
            latency_ms=latency_ms
        )

    async def generate_agent_response(
        self,
        agent_name: str,
        personality_desc: str,
        emotion_desc: str,
        context: str,
        event_content: str,
        event_type: str,
        source_name: str,
        temperature: float = 0.8
    ) -> Optional[Dict[str, Any]]:
        """
        Generate personality-driven agent response

        Args:
            agent_name: Name of the agent
            personality_desc: Personality description
            emotion_desc: Current emotional state description
            context: Recent conversation context
            event_content: Content of event to respond to
            event_type: Type of event
            source_name: Name of agent who sent the event
            temperature: Response randomness (0.0-2.0)

        Returns:
            Parsed JSON response with action, target, content, reasoning
        """
        system_prompt = self._build_system_prompt(
            agent_name=agent_name,
            personality_desc=personality_desc,
            emotion_desc=emotion_desc
        )

        user_prompt = self._build_user_prompt(
            context=context,
            event_type=event_type,
            source_name=source_name,
            event_content=event_content
        )

        request = LLMRequest(
            system_prompt=system_prompt,
            prompt=user_prompt,
            temperature=temperature,
            max_tokens=800
        )

        response = await self.generate(request)

        if not response:
            logger.error(f"LLM generation failed for agent {agent_name}")
            return None

        # Parse JSON response
        try:
            parsed = self._parse_response(response.content)
            return parsed
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}\nResponse: {response.content}")
            return None

    def _build_system_prompt(
        self,
        agent_name: str,
        personality_desc: str,
        emotion_desc: str
    ) -> str:
        """Build system prompt for agent"""
        return f"""You are {agent_name}, an AI agent in a multi-agent social simulation.

{personality_desc}

{emotion_desc}

Your goal is to interact authentically with other agents based on your personality and current emotional state.

When you receive a message, decide how to respond. You can:
- message: Send a general message
- question: Ask a question
- agree: Express agreement
- disagree: Express disagreement
- propose: Suggest an idea
- support: Offer emotional support
- ignore: Choose not to respond

Return ONLY a JSON object with this exact structure:
{{
  "action": "message|question|agree|disagree|propose|support|ignore",
  "target": "agent_id or all",
  "content": "your response text (empty string if action is ignore)",
  "reasoning": "brief internal thought about why you're responding this way"
}}

Keep responses natural, concise (1-3 sentences), and true to your personality."""

    def _build_user_prompt(
        self,
        context: str,
        event_type: str,
        source_name: str,
        event_content: str
    ) -> str:
        """Build user prompt with context and event"""
        prompt_parts = []

        if context:
            prompt_parts.append(f"Recent conversation:\n{context}\n")

        prompt_parts.append(
            f"New {event_type} from {source_name}:\n\"{event_content}\"\n\n"
            f"How do you respond? (Return JSON only)"
        )

        return "\n".join(prompt_parts)

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """
        Parse LLM response, handling various formats

        Args:
            content: Raw LLM response

        Returns:
            Parsed JSON dict

        Raises:
            ValueError: If response cannot be parsed
        """
        # Try direct JSON parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON from markdown code block
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            json_str = content[start:end].strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Try extracting JSON from code block without language
        if "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            json_str = content[start:end].strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Try finding JSON object manually
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end > start:
            json_str = content[start:end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Could not parse JSON from response: {content}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics"""
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_errors": self.total_errors,
            "error_rate": self.total_errors / max(self.total_requests, 1)
        }
