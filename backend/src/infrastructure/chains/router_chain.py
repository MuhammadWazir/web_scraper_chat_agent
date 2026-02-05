from typing import Any, Dict, Optional
import json


class RouterChain:
    def __init__(self, retriever, qa_chain, agent_chain, router_llm):
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

    async def astream(self, inputs, config=None):
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
            async for chunk in self.agent_chain.astream(
                {"input": question, "chat_history": chat_history},
                config=config
            ):
                yield chunk
        else:
            # For QA chain which might not support astream directly or as we want it
            # we could wrap its invoke or use it if it supports astream
            if hasattr(self.qa_chain, "astream"):
                async for chunk in self.qa_chain.astream(question):
                    yield chunk
            else:
                result = await self.qa_chain.ainvoke(question)
                if isinstance(result, dict):
                    answer = result.get("result", result.get("output", str(result)))
                else:
                    answer = str(result)
                yield json.dumps({"type": "content", "data": answer})

