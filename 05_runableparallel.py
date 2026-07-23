from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

import constant
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from dotenv import load_dotenv

load_dotenv()

def runableParallel():
    tokyo_prompt = PromptTemplate(
        template="请帮助我将{text},翻译成日语",
        input_variables=['text'],
    )

    en_prompt = PromptTemplate(
        template="请帮助我将{text},翻译成英语",
        input_variables=['text'],
    )

    model = ChatOpenAI(
        base_url=os.getenv(constant.DEEPSEEK_BASE_URL_CONSTANT),
        api_key=os.getenv(constant.DEEPSEEK_API_KEY_CONSTANT),
        model=os.getenv(constant.DEEPSEEK_MODEL_CONSTANT)
    )

    parser = StrOutputParser()

    en_chain = en_prompt | model | parser
    tokyo_chain = tokyo_prompt | model | parser

    map_chain = RunnableParallel(en=en_chain, chinese=tokyo_chain)

    res = map_chain.invoke({"text": "今天是美好的一天!"})

    print(res)

def call_llm():
    runableParallel()



if __name__ == '__main__':
    call_llm()
