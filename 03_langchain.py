from http import client

from dotenv import load_dotenv
import os
from langchain_core.messages import SystemMessage, HumanMessage, content
from langchain_core.output_parsers import JsonOutputParser

import constant
from langchain_openai import ChatOpenAI
import asyncio
from pydantic import BaseModel, Field

load_dotenv()


async def cll_llm():
    client = ChatOpenAI(
        # API KEY
        api_key=os.getenv(constant.DEEPSEEK_API_KEY_CONSTANT),
        # 基础URL
        base_url=os.getenv(constant.DEEPSEEK_BASE_URL_CONSTANT),
        # 模型
        model=os.getenv(constant.DEEPSEEK_MODEL_CONSTANT)
    )

    # invoke 参数 str, [Any],
    # res = client.invoke("你是什么模型？")
    # res = client.invoke([
    #     # 系统提示词
    #     SystemMessage("请已孙悟空的语气跟我对话，请注意我说的是语气，并不只是指你是孙悟空。"),
    #     # 用户提示词
    #     HumanMessage("你能帮助我做什么？")
    # ])
    # res = client.invoke([
    #     ("system", "请已妲己的语气跟我对话，请注意我说的是语气，并不只是指你是妲己。"),
    #     ("user", "你能帮助我做什么")
    # ])
    # res = client.invoke([
    #     {
    #         "role": 'system',
    #         "content": "你是一个历史学家"
    #     },
    #     {
    #         "role": 'user',
    #         "content": "列出古代十大美女"
    #     }
    # ])

    res = await client.ainvoke([
        {
            "role": 'system',
            "content": "你是一个历史学家"
        },
        {
            "role": 'user',
            "content": "列出古代十大美女"
        }
    ])

    print(res.content)

def call_llm_stream():
    client = ChatOpenAI(
        # API KEY
        api_key=os.getenv(constant.DEEPSEEK_API_KEY_CONSTANT),
        # 基础URL
        base_url=os.getenv(constant.DEEPSEEK_BASE_URL_CONSTANT),
        # 模型
        model=os.getenv(constant.DEEPSEEK_MODEL_CONSTANT),
    )

    # res = client.stream([
    #     SystemMessage("你是一个历史学家"),
    #     HumanMessage("金瓶梅主要讲的是什么")
    # ])

    # 批量调用
    # res = client.batch([
    #     "中国历史上的十大武将",
    #     "满清十大酷刑"
    # ])

    # 大模型使用 pydantic 格式化
    class User(BaseModel):
        name: str = Field(description="成语"),
        age: str = Field(description="来源"),
        address: str = Field(description="居住地址")

    # json_parse = JsonOutputParser(pydantic_object=User)
    #
    # res = client.invoke([
    #     ("system", json_parse.get_format_instructions()),
    #     ("user", "我叫倪宇航，今年20岁，家住反斗花园。")
    # ])
    #
    # res_dict = json_parse.invoke(res)

    # print(res_dict)

    new_client = client.with_structured_output(schema=User)

    res = new_client.invoke("我叫倪宇航，今年20岁，家住反斗花园。")

    print(res)

def main():
    # asyncio.run(cll_llm())
    call_llm_stream()

if __name__ == "__main__":
    main()
