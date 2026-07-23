from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv
import os

from langgraph.checkpoint.memory import InMemorySaver

import constant

load_dotenv()

def agent_memory():
    llm = ChatOpenAI(
        api_key=os.getenv(constant.DEEPSEEK_API_KEY_CONSTANT),
        base_url=os.getenv(constant.DEEPSEEK_BASE_URL_CONSTANT),
        model=os.getenv(constant.DEEPSEEK_MODEL_CONSTANT)
    )

    checkpointer = InMemorySaver()

    agent = create_agent(model=llm,checkpointer=checkpointer)

    agent.invoke({
        "messages": [
            HumanMessage("我的名字是哪吒。")
        ],
    }, config={
            "configurable": {
                "thread_id": "123"
            }
        })

    res = agent.invoke({
        "messages": [
            HumanMessage("你知道我是谁吗？")
        ],
    }, config={
        "configurable": {
            "thread_id": "123",
        }
    })

    print(res)


if __name__ == '__main__':
    agent_memory()