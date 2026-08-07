import json
import logging
import re
import requests
import asyncio
import concurrent.futures

from bs4 import BeautifulSoup
from cloakbrowser import launch
from ddgs import DDGS
from sqlalchemy import select

from models.reddit import RedditSubreddit
from core.database import AsyncSessionLocal
from core.config import settings

logger = logging.getLogger(__name__)


class OpenRouterAgent:
    """A modular agent for interacting with OpenRouter API with tool-calling capabilities."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.tools = {}
        self.tools_schema = []
        self.messages = []

    def register_tool(self, func, description: str, parameters: dict):
        """Registers a Python function as a tool the AI can call."""
        name = func.__name__
        self.tools[name] = func
        self.tools_schema.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                },
            }
        )

    def _call_api(self):
        """Internal method to make the HTTP request to OpenRouter."""
        payload = {
            "model": self.model,
            "messages": self.messages,
        }
        if self.tools_schema:
            payload["tools"] = self.tools_schema

        # Use an ephemeral session to handle connection properly without leaking
        with requests.Session() as session:
            response = session.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            return response.json()

    def ask(self, user_prompt: str) -> str:
        """Sends a prompt to the AI and automatically handles any tool calls."""
        self.messages.append({"role": "user", "content": user_prompt})

        response_data = self._call_api()
        response_message = response_data["choices"][0]["message"]

        while response_message.get("tool_calls"):
            self.messages.append(response_message)

            for tool_call in response_message["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_id = tool_call["id"]

                if tool_name in self.tools:
                    try:
                        arguments = json.loads(
                            tool_call["function"]["arguments"]
                        )
                        func = self.tools[tool_name]
                        result = func(**arguments)
                    except Exception as e:
                        logger.error(f"Error executing {tool_name}: {e}")
                        result = f"Error executing {tool_name}: {e}"

                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "content": str(result),
                        }
                    )
                else:
                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "content": f"Error: Tool '{tool_name}' is not registered.",
                        }
                    )

            response_data = self._call_api()
            response_message = response_data["choices"][0]["message"]

        self.messages.append(response_message)
        return response_message.get("content")


def search_duckduckgo(query: str) -> str:
    logger.info(f"--> [AGENT] Executing Web Search for: {query}")
    # Using the proxy from settings
    results = DDGS(proxy=settings.proxy_url).text(query, max_results=5)
    return json.dumps(results)


def _access_webpage(url: str) -> str:
    browser = launch(headless=True, proxy=settings.proxy_url)
    page = browser.new_page()
    page.goto(url)
    html_content = page.content()
    clean_text = re.sub(r"\n+", " ", html_content)
    clean_text = BeautifulSoup(clean_text, "lxml").text
    browser.close()
    return clean_text


def access_webpage(urls: list[str] | str) -> list[dict] | str:
    if isinstance(urls, str):
        urls = [urls]

    max_concurrent = getattr(settings, "max_concurrent_posts", 5)

    content = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max_concurrent
    ) as executor:
        future_to_url = {
            executor.submit(_access_webpage, url): url for url in urls
        }

        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            logger.info(f"--> [AGENT] Accessing Webpage: {url}")
            try:
                content_text = future.result()
            except Exception as e:
                logger.error(f"Failed to access webpage {url}: {e}")
                content_text = (
                    f"There was a problem requesting the page: {str(e)}"
                )

            content.append(
                {
                    "url": url,
                    "content": content_text
                    or "There was a problem requesting the page",
                }
            )

    return content


async def run_agent_search(
    keyword: str, model: str | None = None
) -> list[dict]:
    """
    Run the agent to search for subreddits matching a keyword.
    Intended to be run in a threadpool since it is synchronous.
    """
    if not model:
        model = "openai/gpt-4o-mini-2024-07-18"

    agent = OpenRouterAgent(
        api_key=settings.openrouter_api_key,
        model=model,
    )

    # agent.register_tool(
    #     func=search_duckduckgo,
    #     description="Searches the web using DuckDuckGo to get up-to-date information.",
    #     parameters={
    #         "type": "object",
    #         "properties": {
    #             "query": {
    #                 "type": "string",
    #                 "description": "The search query.",
    #             }
    #         },
    #         "required": ["query"],
    #     },
    # )

    # agent.register_tool(
    #     func=access_webpage,
    #     description="Accesses the webpages provided and returns their content.",
    #     parameters={
    #         "type": "object",
    #         "properties": {
    #             "urls": {
    #                 "type": "array",
    #                 "items": {"type": "string"},
    #                 "description": "The URLs of the webpages you want to access.",
    #             }
    #         },
    #         "required": ["urls"],
    #     },
    # )

    async with AsyncSessionLocal() as session:
        stmt = select(RedditSubreddit.name, RedditSubreddit.description)
        result = await session.execute(stmt)
        all = result.all()
        subreddits = [
            {"name": r.name, "description": r.description} for r in all
        ]

    prompt = f"""
    Pick the most likely subreddits that match the keyword(s) "{keyword}".

    Choose from these available Subreddits: {subreddits}

    Return ONLY valid JSON (no markdown fences) in this exact structure:
    {{
        "subreddits": [
            {{"subreddit": "r/subreddit"}}
        ]
    }}
    """

    logger.info(f"Asking agent about keyword: {keyword} with model {model}")
    answer = agent.ask(prompt)

    # Clean answer in case AI wraps it in markdown fences
    answer = answer.strip()
    if answer.startswith("```json"):
        answer = answer[7:]
    if answer.startswith("```"):
        answer = answer[3:]
    if answer.endswith("```"):
        answer = answer[:-3]
    answer = answer.strip()
    try:
        data = json.loads(answer)
        subreddits = data.get("subreddits", [])

        # Get list of subreddit names from AI response
        ai_sub_names = []
        for s in subreddits:
            sub_name = s.get("subreddit", "").strip()
            # Remove prefix
            if sub_name.startswith("r/"):
                sub_name = sub_name[2:]

            if sub_name:
                ai_sub_names.append(sub_name)

        cleaned_subs = []
        if ai_sub_names:
            # Query the database for matching subreddits to get their details
            async with AsyncSessionLocal() as session:
                stmt = select(
                    RedditSubreddit.name,
                    RedditSubreddit.description,
                    RedditSubreddit.subscribers,
                    RedditSubreddit.activity_level
                ).where(RedditSubreddit.name.in_(ai_sub_names))
                result = await session.execute(stmt)
                
                # Map the results for quick lookup
                db_subs_map = {
                    r.name: {
                        "description": r.description,
                        "subscribers": r.subscribers,
                        "activity_level": r.activity_level
                    }
                    for r in result.all()
                }

            # Build the final response list matching the frontend's expected format
            for name in ai_sub_names:
                db_data = db_subs_map.get(name, {})
                cleaned_subs.append({
                    "name": name,
                    "description": db_data.get("description"),
                    "subscribers": db_data.get("subscribers"),
                    "activity_level": db_data.get("activity_level"),
                })

        return cleaned_subs
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse agent JSON response: {answer}")
        raise ValueError(f"AI returned invalid JSON: {str(e)}")


async def run_agent_search_task(
    ctx, keyword: str, model: str | None = None
) -> list[dict]:
    """
    ARQ background task wrapper for run_agent_search.
    """
    return await run_agent_search(keyword, model)
