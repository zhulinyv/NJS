# nonebot_plugin_wantwords
# contributor: Limnium

import asyncio, httpx
async def getWords(m, q):
    url = r'https://wantwords.net/{}RD/?q={}&m={}' # q=描述；m=输入语言+目标语言；RD之前为目标语言
    lang={'zhzh':('Chinese','ZhZh'),'enzh':('Chinese','EnZh'),'zhen':('English','ZhEn'),'enen':('English','EnEn')}
    try:
        targetLang=lang[m.lower()][0]
        m=lang[m.lower()][1]
    except:
        return '输入错误，仅支持zhzh/enzh/zhen/enen！' # zh为中文，en为英文。前为输入语言，后为目标语言
    async with httpx.AsyncClient() as client:
        re = await client.get(url=url.format(targetLang,q,m))
    if re.status_code == 200:
        re = re.json()
        return [i['w'] for i in re]
    else:
        return '响应异常'
