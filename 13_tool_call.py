from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import constant

load_dotenv()

@tool(description="获取电脑配置")
def get_info():
    return "显卡是4070,CPU是i7-12400KF，内存32GB。"

def chat():
    llm = ChatOpenAI(
        # API KEY
        api_key=os.getenv(constant.DEEPSEEK_API_KEY_CONSTANT),
        # 基础URL
        base_url=os.getenv(constant.DEEPSEEK_BASE_URL_CONSTANT),
        # 模型
        model=os.getenv(constant.DEEPSEEK_MODEL_CONSTANT)
    )

    llm = llm.bind_tools([get_info])

    message_list = [
        HumanMessage("帮助我查询一下我的电脑配置。")
    ]

    res = llm.invoke(message_list)

    message_list.append(res)

    print(res)

    tool_call = res.tool_calls[0]

    tool_res = get_info.invoke(tool_call)

    message_list.append(ToolMessage(
        content=tool_res,
        tool_call_id=tool_call['id']
    ))

    res = llm.invoke(message_list)

    print(res)


if __name__ == '__main__':
    chat()