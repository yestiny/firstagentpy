from langchain_openai import ChatOpenAI
from config.config import get_config

def main():

    api_config = get_config()

    print(api_config["api_key"][:5] + "*****")

    """参考百炼文档实现https://bailian.console.aliyun.com/cn-beijing/?spm=5176.12818093_47.overview_recent.1.7fa82cc9Fv7yKk&tab=api#/api/?type=model&url=2833609"""

    llm = ChatOpenAI(
        api_key=api_config["api_key"],
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-plus-2025-07-14",
    )

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你是谁？"}]


    """一次性输出res = llm.invoke(messages)
    print(res.model_dump_json())"""


    """流式输出"""

    res = llm.stream(messages)

    for chunk in res:
        print(chunk.model_dump_json())

if __name__ == "__main__":
    main()

