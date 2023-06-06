# python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/22 14:17
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : run.py
# @Software: PyCharm

# @Time    : 2023/01/19 21:00
# @UpdateBy: Limnium
# 更新了正则的pattern，完善了返回机制，“优化”代码风格。
import re
import httpx

codeType = {
    'py': ['python', 'py'],
    'cpp': ['cpp', 'cpp'],
    'java': ['java', 'java'],
    'php': ['php', 'php'],
    'js': ['javascript', 'js'],
    'c': ['c', 'c'],
    'c#': ['csharp', 'cs'],
    'go': ['go', 'go'],
    'asm': ['assembly', 'asm']
}


async def run(strcode):
    strcode = strcode.replace('&amp;', '&').replace('&#91;', '[').replace('&#93;', ']')
    try:
        a = re.match(r'(py|php|java|cpp|js|c#|c|go|asm)\b ?(.*)\n((?:.|\n)+)', strcode)
        lang, stdin, code = a.group(1), a.group(2).replace(' ', '\n'), a.group(3)
    except:
        return "输入有误，目前仅支持c/cpp/c#/py/php/go/java/js"
    dataJson = {
        "files": [
            {
                "name": f"main.{codeType[lang][1]}",
                "content": code
            }
        ],
        "stdin": stdin,
        "command": ""
    }
    headers = {"Authorization": "Token 0123456-789a-bcde-f012-3456789abcde",
               "content-type": "application/"}
    async with httpx.AsyncClient() as client:
        res = await client.post(url=f'https://glot.io/run/{codeType[lang][0]}?version=latest', headers=headers, json=dataJson)
    if res.status_code == 200:
        res = res.json()
        return res['stdout']+('\n---\n'+res['stderr'] if res['stderr'] else '')
    else:
        return '响应异常'
