from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser

import constant
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from dotenv import load_dotenv

load_dotenv()


def call_llm():
    # client = ChatOpenAI(
    #     base_url=os.getenv(constant.DEEPSEEK_BASE_URL_CONSTANT),
    #     api_key=os.getenv(constant.DEEPSEEK_API_KEY_CONSTANT),
    #     model=os.getenv(constant.DEEPSEEK_MODEL_CONSTANT)
    # )

    # prompt_template = ChatPromptTemplate.from_messages(
    #     messages=[
    #         ("system", "你是一个专业的评论员."),
    #         ("human", "请从{action}和{daode}两方面出发,评级一下{name}这个人.")
    #     ]
    # )

    # user_prompt = prompt_template.invoke({"action": "行为", "daode": "道德", "name": "潘金莲"})

    # res = client.invoke(user_prompt)

    # print(res)

    prompt = PromptTemplate(
        template="我想要养一只宠物,是养{p1}好,还是{p2}好?",
        input_variables=['p1', 'p2'],
    )

    model = ChatOpenAI(
        base_url=os.getenv(constant.DEEPSEEK_BASE_URL_CONSTANT),
        api_key=os.getenv(constant.DEEPSEEK_API_KEY_CONSTANT),
        model=os.getenv(constant.DEEPSEEK_MODEL_CONSTANT)
    )

    parser = StrOutputParser()

    chain = prompt | model | parser

    res = chain.invoke({"p1": "狗", "p2": "猫"})

    print(res)


if __name__ == '__main__':
    call_llm()
