"""OpenAI LLM client implementation - FINAL FIX"""
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
        """Create an embedding for text"""
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
        """Create embeddings for multiple texts"""
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
        """Summarize multiple chunks in parallel"""
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
        """
        Create a RAG chain using modern LangChain LCEL API.
        If tools are provided, wrap in RouterChain for agent capabilities.
        """
        settings = load_settings()

        # Prepare chat history and company context
        history_text = format_chat_history(chat_history) if chat_history else ""
        company_context = f"You are a representative of {company_name}. " if company_name else ""

        # Create the LLM
        model = ChatOpenAI(
            model="gpt-5-mini",
            api_key=settings.openai_api_key
        )

        prompt_template = (
            f"{company_context}"
            "Use the following context to answer the question. "
            "If you don't know, say you don't know.\n\n"
            f"{history_text}\n"
            "Context:\n{context}\n\n"
            "Question:\n{input}\n\n"
            "Helpful Answer:"
        )

        prompt = ChatPromptTemplate.from_template(prompt_template)

        # Create the document chain using the modern API
        document_chain = create_stuff_documents_chain(
            llm=model,
            prompt=prompt
        )

        # Create the retrieval chain
        qa_chain = ModernRetrievalChain(
            retriever=retriever,
            document_chain=document_chain
        )

        # If no tools, return the QA chain
        if not tools:
            return qa_chain

        # Build Agent Runnable for tool orchestration
        agent_chain = AgentRunnable(
            client=self.client,
            retriever=retriever,
            tools_config=tools,
            chat_history=chat_history,
            company_name=company_name,
            model=self.default_model
        )

        # Router chain combines RAG + Agent decision
        return RouterChain(
            retriever=retriever,
            qa_chain=qa_chain,
            agent_chain=agent_chain,
            router_llm=self
        )


# ======================================================
# MODERN RETRIEVAL CHAIN (LCEL-based)
# ======================================================

class ModernRetrievalChain:
    """
    Modern retrieval chain using LCEL that properly handles documents.
    """
    def __init__(self, retriever, document_chain):
        self.retriever = retriever
        self.document_chain = document_chain
    
    async def ainvoke(self, inputs: Any, config: Optional[Dict] = None) -> Dict[str, str]:
        """
        Invoke the chain with a query.
        """
        # Handle different input formats
        if isinstance(inputs, str):
            query = inputs
        elif isinstance(inputs, dict):
            query = inputs.get("input") or inputs.get("query", "")
        else:
            query = str(inputs)
        
        try:
            # Retrieve documents
            docs = await self.retriever.ainvoke(query)
            
            # Invoke document chain
            result = await self.document_chain.ainvoke({
                "input": query,
                "context": docs
            })
            
            # Wrap result in dict
            return {"result": result}
            
        except Exception as e:
            return {"result": f"Error processing query: {str(e)}"}
    
    def invoke(self, inputs: Any, config: Optional[Dict] = None) -> Dict[str, str]:
        """Synchronous version (fallback)"""
        import asyncio
        return asyncio.run(self.ainvoke(inputs, config))


# ======================================================
# GENERIC ENDPOINT EXECUTION
# ======================================================

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
    inputs = endpoint.get("inputs", {})

    # Headers
    for key in inputs.get("headers", {}):
        if key in args:
            headers[key] = args[key]

    # Path params
    for key in inputs.get("path", {}):
        url = url.replace(f"{{{key}}}", str(args[key]))

    # Query params
    for key, schema in inputs.get("query", {}).items():
        if key in args:
            params[key] = args[key]
        elif "default" in schema:
            params[key] = schema["default"]

    # Body
    for key in inputs.get("body", {}):
        if key in args:
            body[key] = args[key]

    # Auth
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
        response.raise_for_status()
        return response.json() if response.content else {}
    except Exception as e:
        return {"error": str(e)}


# ======================================================
# TOOL SCHEMA BUILDER - FIXED VERSION
# ======================================================

def build_tools_schema(endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build OpenAI function calling schema from endpoint configurations.
    
    FIXED: Added proper type checking and error handling for malformed tool configs.
    """
    tools = []

    for ep in endpoints:
        # FIXED: Validate that ep is a dict
        if not isinstance(ep, dict):
            print(f"[WARNING] Skipping invalid endpoint (not a dict): {type(ep)}")
            continue
            
        properties = {}
        required = []

        # FIXED: Safely get inputs, default to empty dict
        inputs = ep.get("inputs", {})
        
        # FIXED: Validate inputs is a dict
        if not isinstance(inputs, dict):
            print(f"[WARNING] Endpoint '{ep.get('name', 'unknown')}' has invalid inputs (not a dict): {type(inputs)}")
            inputs = {}

        # FIXED: Iterate safely with proper type checking
        for section_name, section in inputs.items():
            # FIXED: Check that section is a dict
            if not isinstance(section, dict):
                print(f"[WARNING] Section '{section_name}' is not a dict: {type(section)}")
                continue
                
            for name, schema in section.items():
                # FIXED: Check that schema is a dict
                if not isinstance(schema, dict):
                    print(f"[WARNING] Schema for '{name}' is not a dict: {type(schema)}")
                    continue
                    
                properties[name] = {"type": schema.get("type", "string")}
                if schema.get("required"):
                    required.append(name)

        # FIXED: Validate required fields exist
        name = ep.get("name")
        description = ep.get("description", "")
        
        if not name:
            print(f"[WARNING] Skipping endpoint without name: {ep}")
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


# ======================================================
# AGENT RUNNABLE - FIXED VERSION
# ======================================================

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

        # FIXED: Validate tools_config before building schema
        if not isinstance(tools_config, list):
            print(f"[ERROR] tools_config is not a list: {type(tools_config)}")
            self.tool_definitions = []
            self.endpoint_map = {}
        else:
            self.tool_definitions = build_tools_schema(tools_config)
            # FIXED: Build endpoint map with validation
            self.endpoint_map = {}
            for t in tools_config:
                if isinstance(t, dict) and "name" in t:
                    self.endpoint_map[t["name"]] = t

    async def ainvoke(self, input_data: Any, config: Optional[Dict] = None) -> Dict[str, Any]:
        question = input_data if isinstance(input_data, str) else input_data.get("input", "")
        auth_token = (config or {}).get("configurable", {}).get("auth_token")

        # Retrieve context
        docs = await self.retriever.ainvoke(question)
        context = "\n\n".join(d.page_content for d in docs)

        history = format_chat_history(self.chat_history)
        company_context = f"You are a representative of {self.company_name}. " if self.company_name else ""

        system_prompt = (
            f"{company_context}"
            "You are an API orchestration agent. "
            "Use tool outputs as factual truth. "
            "Only use values returned by tools.\n\n"
            f"Context:\n{context}\n\n"
            f"Chat History:\n{history}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]

        # FIXED: Check if we have valid tools before using them
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


# ======================================================
# ROUTER CHAIN
# ======================================================

class RouterChain:
    """
    Always run RAG, then decide if the query requires agent actions.
    """
    def __init__(self, retriever, qa_chain, agent_chain, router_llm: LLMClient):
        self.retriever = retriever
        self.qa_chain = qa_chain
        self.agent_chain = agent_chain
        self.router_llm = router_llm

    async def ainvoke(self, inputs, config=None):
        # Handle input
        if isinstance(inputs, dict):
            question = inputs.get("input", "")
            chat_history = inputs.get("chat_history", [])
        else:
            question = str(inputs)
            chat_history = []

        # 1. Retrieve context
        docs = await self.retriever.ainvoke(question)
        context = "\n".join(d.page_content for d in docs)

        # 2. Router decision prompt
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

        # 3. Route
        if decision_json.get("action_required", False):
            return await self.agent_chain.ainvoke(
                {"input": question, "chat_history": chat_history},
                config=config
            )

        # 4. Answer via RAG
        result = await self.qa_chain.ainvoke(question)
        return result