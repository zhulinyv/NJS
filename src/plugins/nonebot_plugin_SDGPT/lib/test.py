



list_new = ['QQQ;222','WWW;3333']

dict_new = {i.split(';')[1]: i.split(';')[0] for i in list_new}
print(dict_new)