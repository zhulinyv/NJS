class DATA_PANDS:
    def __init__(self, data_dict: dict) -> None:
        self.new_data = {}
        self.data_dict = data_dict
        for key in data_dict:
            self.dict_pan(key)

    def dict_pan(self, key):
        """dict转化为图像所需要的dict量化"""
        # 删除不必要的数据
        if key == "刷特模式":
            self.data_dict.pop(key)
        elif key == "游戏模式" or key == "特感数量" or key == "刷新间隔":
            for item in self.data_dict[key]:
                if item in self.new_data:
                    self.new_data[item] += 1
                else:
                    self.new_data[item] = 1
