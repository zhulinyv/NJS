#兽音译者，一种将“呜嗷啊~”四个字符，通过特殊算法，将明文进行重新组合的加密算法。一种新的咆哮体加密算法。还可以将四个字符任意换成其它的字符，进行加密。

class HowlingAnimalsTranslator:

    __animalVoice="嗷呜啊~"

    def __init__(self,newAnimalVoice=None):
        self.setAnimalVoice(newAnimalVoice)

    def convert(self,txt=""):
        txt=txt.strip()
        if(txt.__len__()<1):
            return ""
        result=self.__animalVoice[3]+self.__animalVoice[1]+self.__animalVoice[0]
        offset=0
        for t in txt:
            c=ord(t)
            b=12
            while(b>=0):
                hex=(c>>b)+offset&15
                offset+=1
                result+=self.__animalVoice[int(hex>>2)]
                result+=self.__animalVoice[int(hex&3)]
                b-=4
        result+=self.__animalVoice[2]
        return result

    def deConvert(self,txt):
        txt=txt.strip()
        if(not self.identify(txt)):
            return "Incorrect format!"
        result=""
        i=3
        offset=0
        while(i<txt.__len__()-1):
            c=0
            b=i+8
            while(i<b):
                n1=self.__animalVoice.index(txt[i])
                i+=1
                n2=self.__animalVoice.index(txt[i])
                c=c<<4|((n1<<2|n2)+offset)&15
                if(offset==0):
                    offset=0x10000*0x10000-1
                else:
                    offset-=1
                i+=1
            result+=chr(c)
        return result

    def identify(self,txt):
        if(txt):
            txt=txt.strip()
            if(txt.__len__()>11):
                if(txt[0]==self.__animalVoice[3] and txt[1]==self.__animalVoice[1] and txt[2]==self.__animalVoice[0] and txt[-1]==self.__animalVoice[2] and ((txt.__len__()-4)%8)==0):
                    for t in txt:
                        if(not self.__animalVoice.__contains__(t)):
                            return False
                    return True
        return False

    def setAnimalVoice(self,voiceTxt):
        if(voiceTxt):
            voiceTxt=voiceTxt.strip()
            if(voiceTxt.__len__()==4):
                self.__animalVoice=voiceTxt
                return True
        return False

    def getAnimalVoice(self):
        return self.__animalVoice