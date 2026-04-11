import os

print("加载的顶层代码")

def get_config():

    return {
        "api_key": os.getenv("API_KEY_4AGENT"),
        "base_url": os.getenv("BASE_URL_4CHATOPENAI"),
        "model": os.getenv("MODEL_4AGENT"),
    }

if __name__ == "__main__":
    print("用main控制的加载的顶层代码")
    config = get_config()
    print(config)
    