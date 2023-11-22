from nonebot_plugin_templates.template_types import Menus, Menu, Funcs, Func
from nonebot_plugin_templates.templates_render import menu_render

from ..type_store.web_config import common_config
from ..utils import Command_Start


class SparkMenus:
    images: dict = {}
    chat: Menus = Menus(
        menus=Menu(
            "会话",
            des="会话的使用和管理\n下面的所有命令中,带{}号的为需要手动填写的值,括号中的参数为选填.",
            funcs=Funcs(
                Func(name=common_config().public_command + "{chat_name} {question} \n( {photo} )",
                     desc="使用公有会话询问\n-参数:\n--必填:\n---1.chat_name: 会话昵称\n---2.question: 问题\n--选填:\n---1. photo:需要识别的图片内容,只有model为bing时才可以使用,需要跟随文本信息一同发送")
                + Func(name=common_config().private_command + "{chat_name} {question} \n( {photo} )",
                       desc="使用私有会话询问\n-参数:\n--必填:\n---1.chat_name: 会话昵称\n---2.question: 问题\n--选填:\n---1. photo:需要识别的图片内容,只有model为bing时才可以使用,需要跟随文本信息一同发送")
                + Func(
                    name=Command_Start + "chat add -n {chat_name} -m {model}   \n( -p {prompt} -c {command} -auto_pic {bool} -num_limit {int} -pic {bool} -url {bool} -stream {bool} -public )",
                    desc="创建一个新的会话:\n-参数:\n--必填:\n---1.chat_name: 会话名称\n---2.model: 使用的模型名称或者索引数字 \n--选填:\n---1.prompt:\n----使用本地预设,须在预设名称前加'.'号\n----使用自定义预设,直接输入内容\n---2.command: \n----使用本地指令,须在指令名称前加'.'号\n----使用自定义指令,直接输入内容\n---3.auto_pic:是否当字数过多时自动转图片\n---4.num_limit:自动转图片的字数上限\n---5.pic:是否总是文字转图片\n---6.url:是否在图片或流式回复时发送全文链接\n---7.stream:是否流式输出,分段发送结果",
                )
                + Func(
                    name=Command_Start + "chat edit -on {old_name}   \n( -nn {new_name} -m {model} -p {prompt} -c {command} -auto_pic {bool} -num_limit {int} -pic {bool} -url {bool} -stream {bool} -public )",
                    desc="修改一个会话(只会修改选择的参数):\n-参数:\n--必填:\n---1.old_name: 原来的会话名称\n--选填:\n---1.new_name: 新的会话名称\n---2.model: 使用的模型名称或者索引数字 \n---3.prompt: 预设\n---4.command: 指令\n---5.auto_pic:是否当字数过多时自动转图片\n---6.num_limit:自动转图片的字数上限\n---7.pic:是否总是文字转图片\n---8.url:是否在图片或流式回复时发送全文链接\n---9.stream:是否流式输出,分段发送结果",
                )
                + Func(name=Command_Start + "chat list", desc="以图片形式查看会话列表,包括私有列表和公有列表")
                + Func(name=Command_Start + "chat del -n {chat_name}   \n( -public )",
                       desc="删除一个会话:\n-参数:\n--chat_name: 会话名称")
            ),
        )
    )

    model: Menus = Menus(
        menus=Menu(
            "模型",
            des="语言模型: 指会话生成回复所使用的模型,不同模型有不同的特性",
            funcs=Funcs(Func(name=Command_Start + "model list", desc="以图片形式展示所有的可使用的模型及其介绍")),
        )
    )

    prompt: Menus = Menus(
        menus=Menu(
            "预设",
            des="预设: 指每次新对话开始前,优先加载的人格\n下面的所有命令中,带{}号的为需要手动填写的值,括号中的参数为选填.",
            funcs=Funcs(
                Func(
                    name=Command_Start + "prompt add -n {name} -c {content}",
                    desc="添加一个新的预设\n-参数:\n--1.name: 预设名称\n--2.content: 预设内容",
                )
                + Func(
                    name=Command_Start + "prompt del -n {name}",
                    desc="删除一个预设\n-参数:\n--name: 预设名称",
                )
                + Func(
                    name=Command_Start + "prompt list   \n( -p {num} )",
                    desc="以图片形式查看预设列表\n-参数:\n--num: 页数(默认第一页)\n",
                )
                + Func(
                    name=Command_Start + "prompt show -n {name}",
                    desc="以图片形式展示一个预设的完整内容\n-参数:\n--name:预设名称",
                )
            ),
        )
    )

    command: Menus = Menus(
        menus=Menu(
            "指令",
            des="指令: 指自动填充在问题前面的指令,可以用来指定回复的格式或者要求\n下面的所有命令中,带{}号的为需要手动填写的值,括号中的参数为选填.",
            funcs=Funcs(
                Func(
                    name=Command_Start + "command add -n {name} -c {content}",
                    desc="添加一个新的指令\n-参数:\n--1.name: 指令名称\n--2.content: 指令内容",
                )
                + Func(
                    name=Command_Start + "command del -n {name}",
                    desc="删除一个指令\n-参数:\n--name: 指令名称",
                )
                + Func(
                    name=Command_Start + "command list   \n( -p {num} )",
                    desc="以图片形式查看指令列表\n-参数:\n--num: 页数",
                )
                + Func(
                    name=Command_Start + "command show -n {name}",
                    desc="以图片形式展示一个指令的完整内容\n-参数:\n--name:指令名称",
                )
            ),
        )
    )

    @property
    def all(self) -> Menus:
        return self.chat + self.model + self.prompt + self.command

    async def get_menu_image(self, menu_name) -> bytes:
        menus_: Menus = getattr(self, menu_name)
        if menus_:
            if menu_name in self.images.keys():
                return self.images[menu_name]
            else:
                image = await menu_render(menus_, width=850)
                self.images[menu_name] = image
                return image
        else:
            raise Exception("Menu not exist.")

    def get_menu_string(self, menu_name) -> str:
        menus_: Menus = getattr(self, menu_name)
        if menus_:
            result = ""
            for menu_index, menu in enumerate(menus_.menus):
                result += f"[{menu_index + 1}].{menu.name}功能\n详细说明请发送 '{menu_name} help' 查看图片版\n"  # noqa: E501
                for func_index, func in enumerate(menu.funcs):
                    result += f"  ({func_index + 1}): {func.name}\n"
                result += "\n"
            return result
        else:
            raise Exception("Menu not exist.")

    def get_func_string(self, func_name: str):
        if func_name == "private chat":
            return "使用私有会话询问\n-参数:\n--必填:\n---1.chat_name: 会话昵称\n---2.question: 问题\n--选填:\n---1. photo:需要识别的图片内容,只有model为bing时才可以使用,需要跟随文本信息一同发送"

        elif func_name == "public chat":
            return "使用公有会话询问\n-参数:\n--必填:\n---1.chat_name: 会话昵称\n---2.question: 问题\n--选填:\n---1. photo:需要识别的图片内容,只有model为bing时才可以使用,需要跟随文本信息一同发送"

        menu_name, func_name = func_name.split(".")
        menu = getattr(self, menu_name)
        for each_func in menu.menus[0].funcs.funcs:
            if each_func.name.startswith(Command_Start + "{menu_name} {func_name}"):
                return f"格式:{each_func.name}\n\n描述:\n{each_func.desc}"


menus = SparkMenus()
