import asyncio
from typing import Awaitable, Tuple, Union, Any, List, Generator

import openai
from openai.openai_object import OpenAIObject

from .config import gpt3_max_tokens, gpt3_model
from typing import Tuple

def remove_punctuation(text):
    import string
    for i in range(len(text)):
        if text[i] not in string.punctuation:
            return text[i:]
    return ""


def get_chat_response(key: str, preset: str, conversation: list, msg: str) -> Tuple[Any, bool]:
    """
    :param key: 密钥
    :param preset: 人格
    :param conversation: 历史会话
    :param msg: 消息内容
    :return:
    """
    system = [
        {"role": "system", "content": preset}
    ]
    prompt = {"role": "user", "content": msg}
    conversation.append(prompt)
    openai.api_key = key
    try:
        response = openai.ChatCompletion.create(
            model=gpt3_model,
            messages=system + conversation,
            max_tokens=gpt3_max_tokens,
            top_p=1,
        )
        res: str = remove_punctuation(response.choices[0].message.content.strip())
        conversation.append({"role": "assistant", "content": res})
        return response, True
    except Exception as e:
        return f"发生错误: {e}", False
