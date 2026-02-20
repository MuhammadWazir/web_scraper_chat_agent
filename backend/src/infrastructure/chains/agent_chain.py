from typing import Any, Dict, Optional, List, AsyncIterator
from openai import AsyncOpenAI
import json
import asyncio

from src.domain.utils.chat_formatter import format_chat_history
from src.infrastructure.utils.tools_utils import build_tools_schema, execute_endpoint


class AgentRunnable:
    """
    Agent that can call tools with streaming support and status hints.
    Sends hints BEFORE calling tools, not after.
    """

    def __init__(
        self,
        client: AsyncOpenAI,
        retriever,
        tools_config: List[Dict],
        chat_history: Optional[List[Dict]] = None,
        company_name: str = "",
        system_prompt: str = "",
        model: str = "gpt-4o-mini"
    ):
        self.client = client
        self.retriever = retriever
        self.tools = tools_config
        self.chat_history = chat_history or []
        self.company_name = company_name
        self.system_prompt = system_prompt
        self.model = model

        if not isinstance(tools_config, list):
            self.tool_definitions = []
            self.endpoint_map = {}
        else:
            self.tool_definitions = build_tools_schema(tools_config)
            self.endpoint_map = {}
            for t in tools_config:
                if isinstance(t, dict) and "name" in t:
                    self.endpoint_map[t["name"]] = t

    async def ainvoke(self, input_data: Any, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Non-streaming version (kept for compatibility)"""
        question = input_data if isinstance(input_data, str) else input_data.get("input", "")
        auth_token = (config or {}).get("configurable", {}).get("auth_token")

        docs = await self.retriever.ainvoke(question)
        context = "\\n\\n".join(d.page_content for d in docs)

        history = format_chat_history(self.chat_history)
        company_context = f"You are a representative of {self.company_name}. " if self.company_name else ""

        prompt_parts = []

        if company_context:
            prompt_parts.append(company_context)

        if self.system_prompt:
            prompt_parts.append(self.system_prompt)

        prompt_parts.append(f"API token: {auth_token}")
        prompt_parts.append(f"Context:\\n{context}")
        prompt_parts.append(f"Chat History:\\n{history}")

        full_system_prompt = "\\n\\n".join(prompt_parts)

        messages = [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": question}
        ]

        if not self.tool_definitions:
            return {"result": "I don't have access to the required tools to complete this task."}

        while True:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tool_definitions,
                tool_choice="auto"
            )

            msg = response.choices[0].message

            if not msg.tool_calls:
                return {"result": msg.content}

            messages.append(msg)

            for call in msg.tool_calls:
                name = call.function.name
                args = json.loads(call.function.arguments)
                endpoint = self.endpoint_map.get(name)

                result = (
                    await execute_endpoint(endpoint, args, auth_token)
                    if endpoint else {"error": f"Unknown tool: {name}"}
                )

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result)
                })

    async def astream(
        self,
        input_data: Any,
        config: Optional[Dict] = None
    ) -> AsyncIterator[str]:
        """
        Streaming version with status hints BEFORE operations.
        """
        question = input_data if isinstance(input_data, str) else input_data.get("input", "")
        auth_token = (config or {}).get("configurable", {}).get("auth_token")

        # HINT: About to search knowledge base
        yield json.dumps({
            "type": "status_hint",
            "message": f"🔍 Searching {self.company_name}'s knowledge base..."
        })

        # NOW do the retrieval
        docs = await self.retriever.ainvoke(question)
        context = "\\n\\n".join(d.page_content for d in docs)

        history = format_chat_history(self.chat_history)
        company_context = f"You are a representative of {self.company_name}. " if self.company_name else ""

        prompt_parts = []

        if company_context:
            prompt_parts.append(company_context)

        if self.system_prompt:
            prompt_parts.append(self.system_prompt)

        prompt_parts.append(f"API token: {auth_token}")
        prompt_parts.append(f"Context:\\n{context}")
        prompt_parts.append(f"Chat History:\\n{history}")

        full_system_prompt = "\\n\\n".join(prompt_parts)

        messages = [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": question}
        ]

        if not self.tool_definitions:
            yield json.dumps({
                "type": "content",
                "data": "I don't have access to the required tools to complete this task."
            })
            return

        # Agentic loop with tool calls
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # HINT: Analyzing what to do next
            if iteration == 1:
                yield json.dumps({
                    "type": "status_hint",
                    "message": "🤔 Analyzing your request..."
                })

            # Get model response (may include tool calls) — non-streaming decision turn
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tool_definitions,
                tool_choice="auto"
            )

            msg = response.choices[0].message

            # If no tool calls, stream the final response with real token streaming
            if not msg.tool_calls:
                yield json.dumps({
                    "type": "status_hint",
                    "message": "✍️ Writing response..."
                })

                stream = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tool_definitions,
                    tool_choice="none",   # decision already made; skip re-routing
                    stream=True
                )
                async for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield json.dumps({
                            "type": "content",
                            "data": delta
                        })
                return

            # Tool calls detected — execute them
            messages.append(msg)

            async def _run_tool(call) -> tuple:
                name = call.function.name
                args = json.loads(call.function.arguments)
                endpoint = self.endpoint_map.get(name)
                result = (
                    await execute_endpoint(endpoint, args, auth_token)
                    if endpoint
                    else {"error": f"Unknown tool: {name}"}
                )
                return call, name, result

            for call in msg.tool_calls:
                name = call.function.name
                yield json.dumps({
                    "type": "status_hint",
                    "message": f"🔧 Calling {name}..."
                })

            # Run all tool HTTP requests concurrently
            tool_results = await asyncio.gather(*[_run_tool(c) for c in msg.tool_calls])

            for call, name, result in tool_results:
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result)
                })
                yield json.dumps({
                    "type": "status_hint",
                    "message": f"✅ Got results from {name}"
                })

        # Max iterations reached
        yield json.dumps({
            "type": "content",
            "data": "I've reached the maximum number of steps. Please try rephrasing your request."
        })
