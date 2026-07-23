from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv
import os
import constant
from langchain_tavily import TavilySearch

load_dotenv()

tool = TavilySearch(tavily_api_key=os.getenv(constant.TAVILY_API_KEY_CONSTANT))

def create_openai_agent():
    agent = create_agent(
        model=ChatOpenAI(
            api_key=os.getenv(constant.DEEPSEEK_API_KEY_CONSTANT),
            base_url=os.getenv(constant.DEEPSEEK_BASE_URL_CONSTANT),
            model=os.getenv(constant.DEEPSEEK_MODEL_CONSTANT)
        ),
        tools=[tool],
        system_prompt="请调用工具帮助我查询信息。"
    )

    res = agent.invoke({
        "messages": [
            HumanMessage("济南今天的天气怎么样？")
        ]
    })

    print(res)

if __name__ == '__main__':
    create_openai_agent()