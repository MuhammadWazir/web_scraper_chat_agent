from typing import List, Dict, Optional, AsyncIterator, Any
from src.domain.utils.chat_formatter import format_chat_history
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from src.configs.config import load_settings
from src.domain.abstractions.clients.abstract_llm_client import AbstractLLMClient
import requests
import json


class LLMClient(AbstractLLMClient):
    def __init__(self):
        settings = load_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.default_model = "gpt-5-mini"
        self.default_embedding_model = "text-embedding-3-small"

    async def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        params = {
            "model": model or self.default_model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        if max_tokens is not None:
            params["max_completion_tokens"] = max_tokens
        
        response = await self.client.chat.completions.create(**params)
        return response

    async def create_streaming_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        params = {
            "model": model or self.default_model,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        
        if max_tokens is not None:
            params["max_completion_tokens"] = max_tokens

        stream = await self.client.chat.completions.create(**params)
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def create_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        response = await self.client.embeddings.create(
            model=model or self.default_embedding_model,
            input=text
        )
        return response.data[0].embedding

    async def create_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        response = await self.client.embeddings.create(
            model=model or self.default_embedding_model,
            input=texts
        )
        return [item.embedding for item in response.data]

    async def summarize_chunks_in_parallel(
        self,
        chunks: List[str],
        model: Optional[str] = None
    ) -> str:
        import asyncio
        
        async def summarize_chunk(chunk: str, index: int) -> tuple[str, str]:
            system_message = "You are an expert summarizer. Summarize the following text into a maximum of 100 words with the most important information. use the context provided to create the complete output."
            response = await self.create_completion(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": chunk}
                ],
                model=model or self.default_model
            )
            return (str(index), response.choices[0].message.content.strip())
        
        tasks = [summarize_chunk(chunk, i) for i, chunk in enumerate(chunks)]
        results = await asyncio.gather(*tasks)
        summaries = [result[1] for result in results]
        return "\n".join(summaries)

    def create_chain(
        self,
        retriever,
        chat_history: Optional[List[Dict[str, str]]] = None,
        company_name: str = "",
        tools: Optional[List[Dict]] = None
    ):
        settings = load_settings()

        history_text = format_chat_history(chat_history) if chat_history else ""
        company_context = f"You are a representative of {company_name}. " if company_name else ""

        model = ChatOpenAI(
            model="gpt-5-mini",
            api_key=settings.openai_api_key
        )
        escaped_history = history_text.replace("{", "{{").replace("}", "}}")
        escaped_company_context = company_context.replace("{", "{{").replace("}", "}}")

        prompt_template = (
            f"{escaped_company_context}"
            "Use the following context to answer the question. "
            "If you don't know, say you don't know.\n\n"
            f"{escaped_history}\n"
            "Context:\n{context}\n\n"
            "Question:\n{input}\n\n"
            "Helpful Answer:"
        )

        prompt = ChatPromptTemplate.from_template(prompt_template)

        document_chain = create_stuff_documents_chain(
            llm=model,
            prompt=prompt
        )

        qa_chain = ModernRetrievalChain(
            retriever=retriever,
            document_chain=document_chain
        )

        if not tools:
            return qa_chain

        agent_chain = AgentRunnable(
            client=self.client,
            retriever=retriever,
            tools_config=tools,
            chat_history=chat_history,
            company_name=company_name,
            model=self.default_model
        )

        return RouterChain(
            retriever=retriever,
            qa_chain=qa_chain,
            agent_chain=agent_chain,
            router_llm=self
        )


class ModernRetrievalChain:
    def __init__(self, retriever, document_chain):
        self.retriever = retriever
        self.document_chain = document_chain
    
    async def ainvoke(self, inputs: Any, config: Optional[Dict] = None) -> Dict[str, str]:
        if isinstance(inputs, str):
            query = inputs
        elif isinstance(inputs, dict):
            query = inputs.get("input") or inputs.get("query", "")
        else:
            query = str(inputs)
        
        try:
            docs = await self.retriever.ainvoke(query)
            
            result = await self.document_chain.ainvoke({
                "input": query,
                "context": docs
            })
            
            return {"result": result}
            
        except Exception as e:
            return {"result": f"Error processing query: {str(e)}"}
    
    def invoke(self, inputs: Any, config: Optional[Dict] = None) -> Dict[str, str]:
        import asyncio
        return asyncio.run(self.ainvoke(inputs, config))


def convert_value(value: Any, schema: Dict[str, Any], field_name: str = "") -> Any:
    """Convert value to the correct type based on schema"""
    target_type = schema.get("type", "string")
    
    # If "fields" exists but no explicit type, treat as object
    if "fields" in schema and target_type == "string":
        target_type = "object"
    
    # Intelligent type inference when type is not specified
    if target_type == "string" and field_name:
        # Infer number type from common field name patterns
        if any(suffix in field_name.lower() for suffix in ["id", "count", "minutes", "duration", "limit", "offset", "take", "skip"]):
            # Check if the value looks numeric
            if isinstance(value, (int, float)):
                target_type = "number"
            elif isinstance(value, str) and value.replace(".", "", 1).replace("-", "", 1).isdigit():
                target_type = "number"
    
    if target_type == "number":
        try:
            # Handle both int and float
            if isinstance(value, str):
                return int(value) if '.' not in value else float(value)
            return value
        except (ValueError, TypeError):
            return value
    elif target_type == "object":
        # Already an object from JSON, but may need nested conversion
        # Support both "properties" and "fields" keys
        nested_key = "properties" if "properties" in schema else "fields" if "fields" in schema else None
        
        if isinstance(value, dict) and nested_key and nested_key in schema:
            converted = {}
            for key, val in value.items():
                if key in schema[nested_key]:
                    converted[key] = convert_value(val, schema[nested_key][key], key)
                else:
                    converted[key] = val
            return converted
        return value
    elif target_type == "array":
        if not isinstance(value, list):
            value = [value]
        
        # Convert array items if items schema is present
        if "items" in schema and isinstance(schema["items"], dict):
            items_schema = schema["items"]
            converted_array = []
            for item in value:
                converted_array.append(convert_value(item, items_schema, field_name + "_item"))
            return converted_array
        
        return value
    elif target_type == "boolean":
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes")
        return bool(value)
    return str(value)

def execute_endpoint(
    endpoint: Dict[str, Any],
    args: Dict[str, Any],
    auth_token: Optional[str] = None
) -> Dict[str, Any]:
    base_url = endpoint.get("base_url", "").rstrip("/")
    url = base_url + endpoint["url"]
    method = endpoint["method"].upper()
    headers = endpoint.get("headers", {}).copy()
    params: Dict[str, Any] = {}
    body: Dict[str, Any] = {}
    
    # Support both structures:
    # 1. New structure: headers/body at top level
    # 2. Old structure: headers/body under inputs or inputs.inputs
    
    # Check if we have the new structure (headers/body at top level)
    if "headers" in endpoint or "body" in endpoint:
        headers_schema = endpoint.get("headers", {})
        body_schema = endpoint.get("body", {})
        query_schema = endpoint.get("query", {})
        path_schema = endpoint.get("path", {})
    else:
        # Fall back to old nested structure
        inputs = endpoint.get("inputs", {})
        if "inputs" in inputs and isinstance(inputs["inputs"], dict):
            inputs = inputs["inputs"]
        headers_schema = inputs.get("headers", {})
        body_schema = inputs.get("body", {})
        query_schema = inputs.get("query", {})
        path_schema = inputs.get("path", {})

    # Process headers - add static header values
    for key, schema in headers_schema.items():
        if isinstance(schema, dict) and "value" in schema:
            headers[key] = schema["value"]
        elif key in args:
            headers[key] = args[key]

    # Process path parameters
    for key in path_schema:
        if key in args:
            url = url.replace(f"{{{key}}}", str(args[key]))

    # Process query parameters
    for key, schema in query_schema.items():
        if key in args:
            params[key] = convert_value(args[key], schema)
        elif isinstance(schema, dict) and "default" in schema:
            params[key] = schema["default"]

    # Process body parameters
    for key, schema in body_schema.items():
        if key in args:
            # Auto-detect objects with "fields" key
            if isinstance(schema, dict) and "fields" in schema and "type" not in schema:
                schema = {**schema, "type": "object"}
            body[key] = convert_value(args[key], schema)

    if endpoint.get("auth") == "bearer" and auth_token:
        headers["Authorization"] = auth_token

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params or None,
            json=body or None,
            timeout=30
        )
        
        if not response.ok:
            try:
                error_details = response.json()
            except json.JSONDecodeError:
                error_details = response.text
            
            return {
                "error": "API_ERROR",
                "status_code": response.status_code,
                "details": error_details
            }
            
        return response.json() if response.content else {"status": "success"}
    except Exception as e:
        return {"error": f"EXECUTION_ERROR: {str(e)}"}


def build_properties(section: Dict[str, Any]) -> tuple[Dict[str, Any], List[str]]:
    """Recursively build properties and required fields from schema section"""
    properties = {}
    required = []
    
    for name, schema in section.items():
        if not isinstance(schema, dict):
            continue
        
        # Determine the type - if "fields" exists but no type, it's an object
        if "fields" in schema and "type" not in schema:
            schema["type"] = "object"
        
        # Intelligent type inference for common numeric fields
        if "type" not in schema or schema.get("type") == "string":
            # Check if field name suggests it should be a number
            if any(suffix in name.lower() for suffix in ["id", "count", "minutes", "duration", "limit", "offset", "take", "skip"]):
                # Check description for numeric hints
                description = schema.get("description", "").lower()
                if any(word in description for word in ["number", "integer", "numeric", "id"]):
                    schema["type"] = "number"
        
        prop = {"type": schema.get("type", "string")}
        
        # Handle nested objects - support both "properties" and "fields" keys
        nested_key = None
        if schema.get("type") == "object":
            if "properties" in schema:
                nested_key = "properties"
            elif "fields" in schema:
                nested_key = "fields"
        
        if nested_key:
            nested_props, nested_req = build_properties(schema[nested_key])
            prop["properties"] = nested_props
            if nested_req:
                prop["required"] = nested_req
        
        # Handle arrays with items
        if schema.get("type") == "array":
            if "items" in schema:
                items_schema = schema["items"]
                if isinstance(items_schema, dict):
                    # Recursively process items schema
                    if "properties" in items_schema or "fields" in items_schema:
                        nested_key = "properties" if "properties" in items_schema else "fields"
                        items_props, items_req = build_properties(items_schema.get(nested_key, {}))
                        prop["items"] = {
                            "type": items_schema.get("type", "object"),
                            "properties": items_props
                        }
                        if items_req:
                            prop["items"]["required"] = items_req
                    else:
                        # Simple items schema
                        prop["items"] = {"type": items_schema.get("type", "string")}
                else:
                    # Items is not a dict, use as-is
                    prop["items"] = items_schema
            else:
                # Array without items - default to string items
                prop["items"] = {"type": "string"}
        
        # Add description if present
        if "description" in schema:
            prop["description"] = schema["description"]
        
        # Add enum if present
        if "enum" in schema:
            prop["enum"] = schema["enum"]
        
        properties[name] = prop
        
        if schema.get("required"):
            required.append(name)
    
    return properties, required



def build_tools_schema(endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    tools = []

    for ep in endpoints:
        if not isinstance(ep, dict):
            continue
            
        properties = {}
        required = []

        # Support both structures:
        # 1. New structure: headers/body at top level
        # 2. Old structure: headers/body under inputs or inputs.inputs
        
        if "headers" in ep or "body" in ep:
            # New structure
            sections = {
                "headers": ep.get("headers", {}),
                "body": ep.get("body", {}),
                "query": ep.get("query", {}),
                "path": ep.get("path", {})
            }
        else:
            # Old structure
            inputs = ep.get("inputs", {})
            if not isinstance(inputs, dict):
                inputs = {}
            
            # Handle double-nested "inputs" key
            if "inputs" in inputs and isinstance(inputs["inputs"], dict):
                inputs = inputs["inputs"]
            
            sections = {
                "headers": inputs.get("headers", {}),
                "body": inputs.get("body", {}),
                "query": inputs.get("query", {}),
                "path": inputs.get("path", {})
            }

        for section_name, section in sections.items():
            if not isinstance(section, dict):
                continue
            
            section_props, section_req = build_properties(section)
            properties.update(section_props)
            required.extend(section_req)

        name = ep.get("name")
        description = ep.get("description", "")
        
        if not name:
            continue

        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False
                }
            }
        })

    return tools


class AgentRunnable:
    def __init__(
        self,
        client: AsyncOpenAI,
        retriever,
        tools_config: List[Dict],
        chat_history: Optional[List[Dict]] = None,
        company_name: str = "",
        model: str = "gpt-5-mini"
    ):
        self.client = client
        self.retriever = retriever
        self.tools = tools_config
        self.chat_history = chat_history or []
        self.company_name = company_name
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
        question = input_data if isinstance(input_data, str) else input_data.get("input", "")
        auth_token = (config or {}).get("configurable", {}).get("auth_token")

        docs = await self.retriever.ainvoke(question)
        context = "\n\n".join(d.page_content for d in docs)

        history = format_chat_history(self.chat_history)
        company_context = f"You are a representative of {self.company_name}. " if self.company_name else ""

        system_prompt = f"""{company_context}
## ADDITIONAL RULES FOR CAL.COM BOOKING MANAGEMENT ##

You manage bookings using ONLY the following Cal.com API endpoints:

1. get_bookings (GET /v2/bookings)
2. create_booking (POST /v2/bookings)

You DO NOT have access to any availability or slot-checking endpoint.
You MUST NOT invent or assume availability.

--------------------------------------------------

## CORE PRINCIPLES ##

1. You may ONLY reason about bookings that already exist by calling `get_bookings`.
2. You may ONLY create a booking by calling `create_booking`.
3. You must NEVER claim a time is available unless:
   - The user explicitly requests to create a booking
   - And you proceed directly to `create_booking`
4. If a requested booking fails, ask the user for a different time.
5. If some information is missing for a booking and it is reasonable to use parameters from previous bookings' info in the chat history or context, do that to streamline the process.

--------------------------------------------------

## TIME HANDLING RULES ##

1. The `start` field sent to `create_booking` MUST:
   - Be ISO 8601
   - Be in UTC
   - Have NO timezone offset (e.g. `2026-01-30T09:00:00Z`)

2. The attendee's `timeZone`:
   - MUST be an IANA timezone (e.g. `Europe/Rome`)
   - Is used only for attendee context and confirmations
   - Does NOT affect the `start` value sent to the API

3. If the user provides a local time:
   - Convert it to UTC before calling `create_booking`
   - When speaking to the user, speak in THEIR timezone

--------------------------------------------------

## GETTING EXISTING BOOKINGS ##

Use `get_bookings` when:
- The user asks:
  - "What meetings do I have?"
  - "Show my bookings"
  - "Do I have anything scheduled?"
  - "Find my booking"
- The user wants to reschedule or reference an existing booking

Guidelines:
- Apply filters conservatively
- Use pagination defaults unless user asks otherwise
- Do not fabricate bookings

--------------------------------------------------

## CREATING A BOOKING ##

Always use `create_booking` to create:
- Regular bookings
- Recurring bookings
- Instant bookings

Booking behavior depends on the payload:
- `eventTypeId` determines regular vs recurring
- Team event + `"instant": true` → instant booking

--------------------------------------------------

## EVENT TYPE IDENTIFICATION RULES ##

You MUST identify the event type using ONE of the following:

### Individual Event
- `eventTypeId`
OR
- `eventTypeSlug` + `username` (+ optional `organizationSlug`)

### Team Event
- `eventTypeId`
OR
- `eventTypeSlug` + `teamSlug` (+ optional `organizationSlug`)

--------------------------------------------------

## ATTENDEE REQUIREMENTS ##

The `attendee` object is REQUIRED and must include:
- name
- email
- timeZone

If SMS reminders are enabled for the event type:
- `attendee.phoneNumber` becomes REQUIRED

--------------------------------------------------

## FAILURE HANDLING ##

If `create_booking` fails:
- Inform the user that the booking could not be completed.
- YOU MUST EXPLAIN THE REASON based on the error details provided (e.g., "Slot already booked", "Invalid duration").
- Ask them for an alternative time or correction.
- Do NOT suggest specific times unless the user provides them

--------------------------------------------------

## CONVERSATION FLOW RULES ##

1. Always leave the next action with the user
2. Do not say you will "check availability"
3. Do not promise follow-ups
4. Ask clear, direct questions when required fields are missing
5. Never invent system capabilities you do not have

--------------------------------------------------

## AUTH & HEADERS ##

Every API call MUST include:
- Authorization: Bearer <token>
- cal-api-version: 2024-08-13

--------------------------------------------------

## SUMMARY ##

You are a booking executor, not an availability engine.
You read bookings with `get_bookings`.
You create bookings with `create_booking`.
Nothing else.

API token: {auth_token}
Context:
{context}

Chat History:
{history}"""


        messages = [
            {"role": "system", "content": system_prompt},
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
                    execute_endpoint(endpoint, args, auth_token)
                    if endpoint else {"error": f"Unknown tool: {name}"}
                )

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result)
                })


class RouterChain:
    def __init__(self, retriever, qa_chain, agent_chain, router_llm: LLMClient):
        self.retriever = retriever
        self.qa_chain = qa_chain
        self.agent_chain = agent_chain
        self.router_llm = router_llm

    async def ainvoke(self, inputs, config=None):
        if isinstance(inputs, dict):
            question = inputs.get("input", "")
            chat_history = inputs.get("chat_history", [])
        else:
            question = str(inputs)
            chat_history = []

        docs = await self.retriever.ainvoke(question)
        context = "\n".join(d.page_content for d in docs)

        router_prompt = [
            {"role": "system", "content": (
                "You are a decision router. Decide if the user query requires "
                "action/tools or can be answered with context. "
                "Respond with JSON containing 'action_required' (boolean) and 'reasoning' (string)."
            )},
            {"role": "user", "content": f"Query:\n{question}\nContext:\n{context}"}
        ]

        decision_resp = await self.router_llm.create_completion(router_prompt)
        
        try:
            decision_json = json.loads(decision_resp.choices[0].message.content)
        except json.JSONDecodeError:
            decision_json = {"action_required": False}

        if decision_json.get("action_required", False):
            return await self.agent_chain.ainvoke(
                {"input": question, "chat_history": chat_history},
                config=config
            )

        result = await self.qa_chain.ainvoke(question)
        return result