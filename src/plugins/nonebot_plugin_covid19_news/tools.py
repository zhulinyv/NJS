import requests
from typing import Dict


class Area():
    def __init__(self, data):
        self.name = data['name']
        self.today = data['today']
        self.total = data['total']
        self.grade = data['total'].get('grade', '风险未确认')
        self.isUpdated = self.today['isUpdated'] # 是否推送
        wzz_add = data['today'].get('wzz_add')
        self.wzz_add = int(wzz_add) if wzz_add else 0
        self.all_add = self.today['confirm'] + self.wzz_add
        self.children = data.get('children', None)
        if self.all_add == 0:
            self.isUpdated = False



    @property
    def main_info(self):
        update = {True: '', False: '（未更新）'}
        return (f"{self.name}{update[self.today['isUpdated']]}\n新增确诊: {self.today['confirm']}\n新增无症状: {self.wzz_add}")

    def __eq__(self, obj):
        return (isinstance(obj, Area) and self.today == obj.today)


class AreaList(Dict):
    def add(self, data):
        if self.get(data.name) != data:
            self[data.name] = data
            
    def get_data(self,name):
        if name[-1] in ['市', '省']:
            name = name[:-1]
        return self.get(name)

    
class NewsData:
    def __init__(self):
        self.data = AreaList()
        self.time = ''
        self.update_data()

    def update_data(self):
        url="https://api.inews.qq.com/newsqa/v1/query/inner/publish/modules/list?modules=statisGradeCityDetail,diseaseh5Shelf"
        res = requests.get(url)
        assert res.status_code == 200
        data = res.json()['data']['diseaseh5Shelf']


        if data['lastUpdateTime'] != self.time:
            
            self.time = data['lastUpdateTime']
            def get_Data(data):
                
                if isinstance(data, list):
                    for i in data:
                        get_Data(i)

                if isinstance(data, dict):
                    area_ = data.get('children')
                    if area_:
                        get_Data(area_)

                    self.data.add(Area(data))

            get_Data(data['areaTree'][0])
            return True


NewsBot = NewsData()