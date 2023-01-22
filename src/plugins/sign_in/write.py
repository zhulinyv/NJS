import json

async def write_file(coint,qq,first,file_read,time):
    if first == True:
        file_name = 'coints.json'
        data = dict(file_read)
        data2 = {str(qq):coint,f'{qq}login':time}
        data.update(data2)
        print(data)
        with open(file_name,'w') as f:
           json.dump(data,f)
    else:
        file_name = 'coints.json'
        data = dict(file_read)
        qq_str = str(qq)
        print(data)
        coints = data[f'{qq_str}']
        data[f'{qq_str}'] = int(coints) + int(coint)
        data[f'{qq_str}login'] = str(time)
        print(data)
        with open(file_name,'w') as f:
            json.dump(data,f)
