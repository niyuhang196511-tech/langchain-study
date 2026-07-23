from dotenv import load_dotenv
import os

DEEPSEEK_BASE_URL_CONSTANT= "DEEPSEEK_BASE_URL"
DEEPSEEK_API_KEY_CONSTANT="DEEPSEEK_API_KEY"
DEEPSEEK_MODEL_CONSTANT="DEEPSEEK_MODEL"

load_dotenv()

print(os.getenv(DEEPSEEK_BASE_URL_CONSTANT))

def main():
    print("Hello from langchain!")


if __name__ == "__main__":
    main()
