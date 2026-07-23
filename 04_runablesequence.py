from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser

import constant
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from dotenv import load_dotenv

load_dotenv()


def call_llm():
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
