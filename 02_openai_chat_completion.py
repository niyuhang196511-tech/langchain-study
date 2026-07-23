from dotenv import load_dotenv
import os
from openai import OpenAI

DEEPSEEK_BASE_URL_CONSTANT= "DEEPSEEK_BASE_URL"
DEEPSEEK_API_KEY_CONSTANT="DEEPSEEK_API_KEY"
DEEPSEEK_MODEL_CONSTANT="DEEPSEEK_MODEL"

load_dotenv()


def main():
    client = OpenAI(
        base_url=os.getenv(DEEPSEEK_BASE_URL_CONSTANT),
        api_key=os.getenv(DEEPSEEK_API_KEY_CONSTANT),
    )

    response = client.chat.completions.create(
        model=os.getenv(DEEPSEEK_MODEL_CONSTANT),
        messages=[
            {
                "role": "system",
                "content": "你是一个翻译专家，会世界上多种语言。"
            },
            {
                "role": "user",
                "content": "将'你好'翻译成意大利语。"
            }
        ]
    )

    print(response.choices[0].message.content)

if __name__ == "__main__":
    main()
