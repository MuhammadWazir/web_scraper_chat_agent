from typing import Any, Dict, Optional
import asyncio


class RetrievalChain:
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
        return asyncio.run(self.ainvoke(inputs, config))
