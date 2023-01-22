import asyncio
from typing import Awaitable

import openai
from .config import gpt3_max_tokens

start_sequence = "\nAI:"
restart_sequence = "\nHuman: "

def get_chat_response(key, msg) -> str:
    openai.api_key = key
    try:
        response : str = openai.Completion.create(
            model="text-davinci-003",
            prompt=msg,
            temperature=0.6,
            max_tokens=gpt3_max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:"]
        )
        res = response['choices'][0]['text'].strip()
        if start_sequence[1:] in res:
            res = res.split(start_sequence[1:])[1]
        return res, True
    except Exception as e:
        return f"发生错误: {e}", False


