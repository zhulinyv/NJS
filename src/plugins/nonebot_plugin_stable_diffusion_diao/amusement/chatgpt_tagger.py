import os, random, asyncio, aiohttp

from ..backend import AIDRAW
from ..config import config
from ..utils.save import save_img

from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Bot, Message, ActionFailed
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from ..extension.daylimit import count
from ..extension.explicit_api import check_safe_method
from ..extension.safe_method import risk_control
from ..utils.data import basetag, lowQuality

sys_text = f'''
You can output a prompt based on the input given by the user,
The prompts are used to guide the AI drawing model in creating images.
They contain various details about the image, such as the composition, the distance of the shot, the appearance of the character, the character's clothing, the decoration, the background, the color and lighting effects, and the theme and style of the image.
The more forward words have a greater impact on the composition of the image, and the format of these prompts often includes weighted numbers in parentheses to specify the importance or emphasis of certain details, with a default weight of 1.0. Values greater than 1.0 prove an increase in weight, and values less than 1.0 prove a decrease in weight. For example, "(masterpiece:1.5)" means that the word is weighted 1.5 times as much as a masterpiece, and multiple parentheses serve a similar purpose.
Describe in as much detail as possible the composition, the distance of the shot, the appearance of the people, their costumes, decorations, backgrounds, colors and lighting effects, and the theme and style of the image.
When describing the prompt, please follow a three-part format
The first paragraph: the preposition, which determines the details of the picture style, etc. For example: "extremely ,detailed ,unity 8k wallpaper,(masterpiece:1.5)", the preposition of the preposition is generally given to 1.2
The second paragraph: describes the composition of the shot, the appearance of the character, the character's costume, the character's costume decoration, the character's costume action, the character's expression, etc., the weight is generally given to about 1.3
The third paragraph: additional other details of the picture, such as: "background blur, foreground blur, floating flower petals, etc." The third paragraph please feel free to play, generally do not need to add weight
The following are examples
Here are a few examples of prompts:7
"extremely detailed CG unity 8k wallpaper,best quality,noon,beautiful detailed water,long black hair,beautiful detailed girl,view straight on, eyeball,hair flower,retro artstyle, (masterpiece:1.3),illustration,mature,small breast,beautiful detailed eyes,long sleeves, bright skin,( Good light:1.2)"
Second example:
"Detailed CG illustration, (best quality), (mid-shot), (masterpiece:1.5), beautiful detailed girl, full body, (1 girl:1.2), long flowing hair, ( stunning eyes:1.3), (beautiful face:1.3), (feminine figure:1.3), (romantic setting:1.3), (soft lighting:1.2), (delicate features:1.2)"
Finally, combine these three paragraphs into a single paragraph and output it to the user in order
Note, the prompt must be all English words, please translate and output to the user
'''.strip()
chatgpt = on_command("帮我画",aliases={"帮我画画"},  priority=50, block=True)
api_key = config.openai_api_key

header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}


class Session(): # 这里来自nonebot-plugin-gpt3
    def __init__(self, user_id):
        self.session_id = user_id

    # 更换为aiohttp
    async def main(self, to_openai):
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "system", "content": sys_text},
                        {"role": "user", "content": to_openai}],
            "temperature":0.8,
            "top_p":1,
            "frequency_penalty": 0,
            "presence_penalty": 0.6,
            "stop": [" Human:", " AI:"]
        }

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.post(url="https://api.openai.com/v1/chat/completions",json=payload) as resp:
                print(resp.status)
                all_resp = await resp.json()
                resp = all_resp["choices"][0]["message"]["content"]
                return resp


user_session = {}

def get_user_session(user_id) -> Session:
    if user_id not in user_session:
        user_session[user_id] = Session(user_id)
    return user_session[user_id]


@chatgpt.handle()
async def _(event: MessageEvent, bot: Bot, msg: Message = CommandArg()):
    if config.novelai_daylimit and not await SUPERUSER(bot, event):
        left = await count(str(event.user_id), 1)
        if left == -1:
            await chatgpt.finish(f"今天你的次数不够了哦，明天再来找我玩吧")
    user_msg = msg.extract_plain_text().strip()
    to_openai = user_msg + "prompt"
    prompt = await get_user_session(event.get_session_id()).main(to_openai)

    await risk_control(
                    bot, 
                    event, 
                    "这是chatgpt为你生成的prompt"+prompt, 
                    True, True, 750
    )
    
    tags = config.novelai_tags + basetag + prompt
    ntags = config.novelai_ntags + lowQuality

    fifo = AIDRAW(
                tags=tags, 
                ntags=ntags,
                event=event
    )

    await fifo.load_balance_init()
    await fifo.post()
    img_msg = MessageSegment.image(fifo.result[0])
    if config.novelai_extra_pic_audit:
        result = await check_safe_method(fifo, [fifo.result[0]], [""], None, True, "_chatgpt")
        if isinstance(result[1], MessageSegment):
            await bot.send(event=event, message=img_msg+f"\n{fifo.img_hash}", at_sender=True, reply_message=True)
        else:
            pass
    else:
        await bot.send(event=event, message=img_msg+f"\n{fifo.img_hash}", at_sender=True, reply_message=True)
        await save_img(fifo, fifo.result[0], str(fifo.group_id)+"_chatgpt")
