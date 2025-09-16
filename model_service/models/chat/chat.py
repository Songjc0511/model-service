from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key="sk-d71190676bdf424692476e6615880042",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def chat_stream(messages):
    response = client.chat.completions.create(
        model="qwen-max",
        messages=messages,
        stream=True
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            text = chunk.choices[0].delta.content
            print(text, end="", flush=True)
            yield text

def chat(messages):
    response = client.chat.completions.create(
        model="qwen-max",
        messages=messages,
    )
    return response.choices[0].message.content

def chat_wait(messages):
    response = client.chat.completions.create(
        model="qwen-max",
        messages=messages,
    )
    return response.choices[0].message.content
