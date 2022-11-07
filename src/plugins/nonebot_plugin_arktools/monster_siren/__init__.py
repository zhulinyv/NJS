from nonebot import on_command
from nonebot.exception import ActionFailed
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from .data_source import search_cloud, build_image

pickup = on_command("塞壬点歌")  # 点歌(qq音乐)
show_list = on_command("塞壬歌单")  # 查看歌单


@pickup.handle()
async def _(arg: Message = CommandArg()):
    keyword = arg.extract_plain_text().strip()
    if not keyword:
        keyword = "Synthetech"

    music = await search_cloud(keyword)
    if not music:
        await pickup.finish(f"网易云音乐中未找到歌曲 {keyword}", at_sender=True)
    await pickup.finish(music)


@show_list.handle()
async def _():
    image = await build_image()
    img = MessageSegment.image(image)
    try:
        await show_list.finish(Message(img))
    except ActionFailed as e:
        await show_list.finish(f"图片发送失败：{e}")
