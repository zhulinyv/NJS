# nonebot_plugin_wantwords
# contributor: Limnium

from nonebot import on_command, get_driver
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
 
from .config import Config
from .getWords import getWords

wantwords_config = Config.parse_obj(get_driver().config)

wantwords = on_command('找词', aliases={'反向词典','wantwords'},priority=5)

@wantwords.handle()
async def wantwords_body(args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    contents = str(plain_text).split(' ',1)
    if len(contents)!=2 or not contents[1]:
        wantwords.finish('输入有误，正确格式：\n找词 <模式> <描述>')
    re = await getWords(contents[0],contents[1])
    await wantwords.finish('你可能想找'+('; '.join(re[:wantwords_config.wantwords_max_results])),at_sender=True)
