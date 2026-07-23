import asyncio

from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv
import os
import constant
from langchain_tavily import TavilySearch

load_dotenv()

async def call_mcp():
    clint = MultiServerMCPClient({
        "12306": {
            "transport": "streamable_http",
            "url": "https://mcp.api-inference.modelscope.net/e8519543154e44/mcp"
        }
    })

    tools = await clint.get_tools()

    llm = ChatOpenAI(
        api_key=os.getenv(constant.DEEPSEEK_API_KEY_CONSTANT),
        base_url=os.getenv(constant.DEEPSEEK_BASE_URL_CONSTANT),
        model=os.getenv(constant.DEEPSEEK_MODEL_CONSTANT)
    )

    agent = create_agent(model=llm, tools=tools)

    res = await agent.ainvoke({
        "messages": [
            HumanMessage("帮助我查询一下今天从济南到磁窑的火车。")
        ]
    })

    print(res)

if __name__ == '__main__':
    asyncio.run(call_mcp())