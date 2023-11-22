from typing import Optional

from nonebot_plugin_templates.templates_render import dict_render

Classes = []


def register_chatbot(cls):
    global Classes
    Classes.append(cls)
    return cls


from . import  ChatGPTApiBot,ChatGPTWebBot,BingBot,ClaudeAiBot,SlackClaudeBot  # noqa: E402, F401


class ChatBots:
    image_: bytes = None
    dict_hash: Optional[int] = None

    def get_model_class(self, model: str):
        able_models = [key for key, value in self.chatbot_dict.items() if value["able"]]
        if model.isdigit():
            if len(able_models) >= int(model):
                model = able_models[int(model) - 1]
            else:
                raise Exception("模型序号超出总数,请检查后重新输入")
        if model in able_models:
            return self.chatbot_dict[model]["chatbot"]
        else:
            raise Exception(
                f"模型不存在或不可用.\n当前可用模型有: {', '.join(model for model in able_models)}"
            )

    @property
    def chatbot_dict(self):
        c_d = {
            class_.__name__.replace("Bot", ""): {
                "able": class_.able,
                "description": class_.desc,
                "chatbot": class_,
            }
            for class_ in Classes
        }

        return c_d

    async def get_image(self):
        dict_hash = hash(str(self.chatbot_dict))
        if dict_hash == self.dict_hash and self.image_:
            return self.image_
        else:
            data = {
                k: v["description"] for k, v in self.chatbot_dict.items() if v["able"]
            }

            self.image_ = await dict_render(data, title="模型列表")
            self.dict_hash = dict_hash
            return self.image_


chatbots = ChatBots()
