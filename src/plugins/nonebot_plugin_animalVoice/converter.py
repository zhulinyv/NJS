from .AnimalVoice import HowlingAnimalsTranslator

#实例化
animalVoice = HowlingAnimalsTranslator()

#编译
def msg_convert(input):
    msg = animalVoice.convert(input)
    return msg

#反编译
def msg_deconvert(input):
    msg = animalVoice.deConvert(input)
    return msg