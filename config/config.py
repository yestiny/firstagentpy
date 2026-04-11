import os

print("加载的顶层代码")

def get_config():

    return {
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "base_url": os.getenv("ANTHROPIC_BASE_URL"),
        "model": os.getenv("ANTHROPIC_MODEL"),
    }

if __name__ == "__main__":
    print("用main控制的加载的顶层代码")
    config = get_config()
    print(config)
    