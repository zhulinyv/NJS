from typing import Any, Tuple
from .config import gpt3_max_tokens, gpt3_model
import httpx

def remove_punctuation(text):
    import string
    for i in range(len(text)):
        if text[i] not in string.punctuation:
            return text[i:]
    return ""

async def get_chat_response(proxy: str, key: str, preset: str, conversation: list, msg: str) -> Tuple[Any, bool]:
    """
    :param proxy: 代理
    :param key: 密钥
    :param preset: 人格
    :param conversation: 历史会话
    :param msg: 消息内容
    :return:
    """
    if proxy:
        proxies = {
            "http://": proxy,
            "https://": proxy,
        }
    else:
        proxies = {}

    system = [
        {"role": "system", "content": preset}
    ]
    prompt = {"role": "user", "content": msg}
    conversation.append(prompt)
    client = httpx.AsyncClient(proxies=proxies, timeout=None)
    try:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": gpt3_model,
                "messages": system + conversation,
                "max_tokens": gpt3_max_tokens,
            },
        )
        response = response.json()
        try:
            res: str = remove_punctuation(response['choices'][0]['message']['content'].strip())
            conversation.append({"role": "assistant", "content": res})
            return response, True
        except:
            return response, False
    except httpx.ConnectTimeout as e:
        return f"发生HTTP超时错误: {e.request.url}", False
    except Exception as e:
        return f"发生未知错误: {type(e)} {e}", False
