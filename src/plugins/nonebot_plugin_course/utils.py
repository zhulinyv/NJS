import time
import importlib
from PIL import Image
from pathlib import Path
import datetime
import json

from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot import logger, get_driver
from pydantic import error_wrappers

from .template import DefaultTemplate, PicTemplate

"""
代码逻辑：存入数据（字典）→ 读取数据 → 填充表格 → 生成图片
"""


class DataManager(object):
    def __init__(self):
        """
        说明:初始化
        """
        self.course_data = {}

    def load_class_info(self):
        """
        说明:加载课程信息
        :return:
        """
        def load_from_json(_json_path: Path):
            """
            说明:加载json文件
            :param _json_path:
            :return:
            """
            self.course_data = json.loads(_json_path.read_text(encoding='utf-8'))

        try:
            load_from_json(Path.cwd() / 'data' / 'course_config' / 'config.json')
            logger.success(f'课表数据加载成功')
        except json.JSONDecodeError as e:
            logger.opt(colors=True).error(f'<y>课表</y> 课表数据加载失败 <c>(from json)</c>\n'
                                          f'<y>json解析失败</y>: {e}')
        except error_wrappers.ValidationError as e:
            logger.opt(colors=True).error(f'<y>课表</y> 课表数据加载失败 <c>(from json)</c>\n'
                                          f'<y>json缺少必要键值对</y>: \n'
                                          f'{e}')
        return self.course_data


class TemplateManager(object):
    def __init__(self):
        self.template_container = {'default': DefaultTemplate}  # 模板装载对象
        self.templates_path = Path.cwd() / 'menu_config' / 'template'  # 模板路径
        self.load_templates()

    def load_templates(self):  # 从文件加载模板
        template_list = [template for template in self.templates_path.glob('*.py')]
        template_name_list = [template.stem for template in self.templates_path.glob('*.py')]
        for template_name, template_path in zip(template_name_list, template_list):
            template_spec = importlib.util.spec_from_file_location(template_name, template_path)
            template = importlib.util.module_from_spec(template_spec)
            template_spec.loader.exec_module(template)
            self.template_container.update({template_name: template.DefaultTemplate})

    def select_template(self, template_name: str) -> PicTemplate:  # 选择模板
        if template_name in self.template_container:
            return self.template_container[template_name]
        else:
            raise KeyError(f'There is no template named {template_name}')


def get_weekday():
    """
    获取今天是周几
    :return: int
    """
    return datetime.datetime.now().weekday() + 1


def get_rest_time(current, query_time):
    """
    将剩余时间的秒数转为天时分秒（若为0则不显示）
    """
    diff = query_time - current
    d = diff // (24 * 3600)
    dr = diff % (24 * 3600)
    h = dr // 3600
    hr = dr % 3600
    m = hr // 60
    if d is not 0:
        msg = f"{d}天{h}小时{m}分"
        return msg
    elif h is not 0:
        msg = f"{h}小时{m}分"
        return msg
    else:
        msg = f"{m}分钟"
        return msg


class CourseManager(object):
    """
    说明:课表管理类
    """
    def __init__(self):
        self.cwd = Path.cwd()
        self.config_folder_make()
        self.data_manager = DataManager()
        self.template_manager = TemplateManager()
        # 上下课时间
        self.exact_time = {
            "1": {"start": "08:20", "end": "09:05"},
            "2": {"start": "09:10", "end": "09:55"},
            "3": {"start": "10:15", "end": "11:00"},
            "4": {"start": "11:05", "end": "11:50"},
            "5": {"start": "11:55", "end": "12:25"},
            "6": {"start": "12:30", "end": "13:00"},
            "7": {"start": "13:10", "end": "13:55"},
            "8": {"start": "14:00", "end": "14:45"},
            "9": {"start": "15:05", "end": "15:50"},
            "10": {"start": "15:55", "end": "16:40"},
            "11": {"start": "18:00", "end": "18:45"},
            "12": {"start": "18:50", "end": "19:35"},
            "13": {"start": "19:40", "end": "20:25"},
        }

    def config_folder_make(self):
        """
        说明:创建配置文件夹
        :return:
        """
        if not (self.cwd / 'data').exists():
            (self.cwd / 'data').mkdir()
        if not (self.cwd / 'data' / 'course_config').exists():
            (self.cwd / 'data' / 'course_config').mkdir()
        if not (self.cwd / 'data' / 'course_config' / 'fonts').exists():
            (self.cwd / 'data' / 'course_config' / 'fonts').mkdir()
        if not (self.cwd / 'data' / 'course_config' / 'templates').exists():
            (self.cwd / 'data' / 'course_config' / 'templates').mkdir()
        if not (self.cwd / 'data' / 'course_config' / 'menus').exists():
            (self.cwd / 'data' / 'course_config' / 'menus').mkdir()
        # 创建默认字体
        if not (self.cwd / 'data' / 'course_config' / 'config.json').exists():
            with (self.cwd / 'data' / 'course_config' / 'config.json').open('w', encoding='utf-8') as fp:
                fp.write(json.dumps({'default': 'simhei.ttf'}))

    def generate_timetable_image(self, event: GroupMessageEvent, week=None) -> Image:
        """
        说明:生成完整课表图片
        :param event:
        :param week:
        :return:
        """
        self.init_user_data(event)
        if self.init_user_data(event) == -1:
            return f"暂时还没有你的数据哦，请联系超管创建一个你的课表吧"
        user_id = str(event.user_id)
        data = self.data_manager.course_data[user_id]
        template = self.template_manager.select_template('default')
        return template().generate_main_menu(data, event=event, current_week=week)

    def generate_week_image(self, event: GroupMessageEvent, week) -> Image:
        """
        生成当前周数的课表
        :param event:
        :param week:
        :return:
        """
        self.init_user_data(event)
        if self.init_user_data(event) == -1:
            return f"暂时还没有你的数据哦，请联系超管创建一个你的课表吧"
        user_id = str(event.user_id)
        data = self.data_manager.course_data[user_id]
        template = self.template_manager.select_template('default')
        return template().generate_main_menu(data, event=event, current_week=week)

    def init_user_data(self, event: GroupMessageEvent):
        """
        说明:初始化用户数据
        :param event:
        :return:
        """
        user_id = str(event.user_id)
        self.data_manager.course_data = self.data_manager.load_class_info()
        if user_id not in self.data_manager.course_data:
            self.blank_struct(event)
            return -1
        elif "exact_time" not in self.data_manager.course_data[user_id]:
            self.data_manager.course_data[user_id]["exact_time"] = self.exact_time
            self.save()
            self.data_manager.course_data[user_id] = self.data_manager.load_class_info()[user_id]
        else:
            self.data_manager.course_data[user_id] = self.data_manager.load_class_info()[user_id]

    def save(self):
        """
        保存数据
        :return:
        """
        with (self.cwd / 'data' / 'course_config' / 'config.json').open('w', encoding='utf-8') as fp:
            json.dump(self.data_manager.course_data, fp, indent=4, ensure_ascii=False)

    def blank_struct(self, event: GroupMessageEvent):
        """
        新建user的空白课表结构存在json里
        :return:
        """
        user_id = str(event.user_id)
        course_info = {"name": "",
                       "teacher": "",
                       "classroom": "",
                       "week": []}

        # 新用户的周数默认初始化为1
        self.data_manager.course_data[user_id] = {'week': 1,
                                                  'exact_time': {
                                                      "1": {"start": "08:20", "end": "09:05"},
                                                      "2": {"start": "09:10", "end": "09:55"},
                                                      "3": {"start": "10:15", "end": "11:00"},
                                                      "4": {"start": "11:05", "end": "11:50"},
                                                      "5": {"start": "11:55", "end": "12:25"},
                                                      "6": {"start": "12:30", "end": "13:00"},
                                                      "7": {"start": "13:10", "end": "13:55"},
                                                      "8": {"start": "14:00", "end": "14:45"},
                                                      "9": {"start": "15:05", "end": "15:50"},
                                                      "10": {"start": "15:55", "end": "16:40"},
                                                      "11": {"start": "18:00", "end": "18:45"},
                                                      "12": {"start": "18:50", "end": "19:35"},
                                                      "13": {"start": "19:40", "end": "20:25"},
                                                  },
                                                  }
        for i in range(7):
            i += 1
            self.data_manager.course_data[user_id][str(i)] = {}
            for j in range(13):
                j += 1
                self.data_manager.course_data[user_id][str(i)][str(j)] = []
                self.data_manager.course_data[user_id][str(i)][str(j)].append(course_info)

        self.save()

    def auto_update_week(self):
        """
        更新周数
        :return:
        """
        self.data_manager.course_data = self.data_manager.load_class_info()
        tmp_data = self.data_manager.course_data
        users_list = []
        for user_id, value in tmp_data.items():
            try:
                if user_id.isdigit() and value['week']:
                    users_list.append(user_id)
            except KeyError:
                pass
        # py里面似乎没有for(auto)的语法，所以这里先添加了一次用户名单，再挨个更新周数
        for user in users_list:
            self.data_manager.course_data[user]['week'] += 1
        self.save()

    def set_week(self, event, week: int):
        """
        设置周数
        :param event:
        :param week: int
        :return:
        """
        self.init_user_data(event)
        user_id = str(event.user_id)
        self.data_manager.course_data[user_id]['week'] = week
        self.save()

    def get_week(self, event):
        """
        获取周数
        :param event
        :return: int
        """
        self.init_user_data(event)
        user_id = str(event.user_id)
        return self.data_manager.course_data[user_id]['week']

    def now_course(self, event):
        """
        获取当前课程及最近的一节课(今日范围内)
        :param event:
        :return:
        """
        # 获取当前周数
        current_week = self.get_week(event)

        # 获取当前是周几
        current_weekday = get_weekday()

        # 获取当前格式化时间
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = ""

        # 取前十位到日期
        current_day = now_time[:10]

        # 当前时间戳
        current_time_stamp = int(time.mktime(time.strptime(now_time, '%Y-%m-%d %H:%M:%S')))
        today_data = self.data_manager.course_data[str(event.user_id)][str(current_weekday)]
        user_exact_time = self.data_manager.course_data[str(event.user_id)]["exact_time"]
        is_in_class = 0
        next_class = 0
        try:
            row_num = get_driver().config.row_num
        except:
            row_num = 13
        for i in range(1, row_num + 1):
            # 今日上下课时间
            course_start_time = f"{current_day} {user_exact_time[str(i)]['start']}"  # 注意有空格
            course_end_time = f"{current_day} {user_exact_time[str(i)]['end']}"

            # 今日上下课时间的时间戳
            course_start_time_stamp = int(time.mktime(time.strptime(course_start_time, '%Y-%m-%d %H:%M')))
            course_end_time_stamp = int(time.mktime(time.strptime(course_end_time, '%Y-%m-%d %H:%M')))
            for course in today_data[str(i)]:
                if course_start_time_stamp <= current_time_stamp <= course_end_time_stamp\
                        and current_week in course['week']:
                    msg += f"当前您正在上第{i}节课,为{course['name']},地点为{course['classroom']}\n还有{get_rest_time(current_time_stamp, course_end_time_stamp)}下课 "
                    is_in_class = 1
                    break
            for course in today_data[str(i)]:
                if current_time_stamp < course_start_time_stamp and current_week in course['week'] and next_class == 0:
                    msg += f"今天的下一节课为{course['name']},地点为{course['classroom']}\n,上课时间为{user_exact_time[str(i)]['start']}\n还有{get_rest_time(current_time_stamp, course_start_time_stamp)}上课，请注意不要迟到 "
                    next_class = 1
                    break
            if is_in_class == 1 and next_class == 1:
                break

        if is_in_class == 0:
            msg = f"当前没有正在上的课\n" + msg

        if next_class == 0:
            msg = msg + f"今天剩下没有课了哦"
        weekday_info = ""
        if current_weekday == 1:
            weekday_info = "星期一"
        elif current_weekday == 2:
            weekday_info = "星期二"
        elif current_weekday == 3:
            weekday_info = "星期三"
        elif current_weekday == 4:
            weekday_info = "星期四"
        elif current_weekday == 5:
            weekday_info = "星期五"
        elif current_weekday == 6:
            weekday_info = "星期六"
        elif current_weekday == 7:
            weekday_info = "星期日"
        tmp = f"当前时间为{now_time},第{current_week}周{weekday_info}\n"
        msg = tmp + msg
        return msg

    def tomo_course(self, event):
        """
        获取明天第一节课的情报
        :param event:
        :return:
        """
        # 获取当前周数
        current_week = self.get_week(event)

        # 获取当前是周几
        current_weekday = get_weekday()

        if current_weekday != 7:
            current_weekday += 1
        else:
            current_weekday = 1
            current_week += 1

        # 获取当前格式化时间
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = ""

        # 获取明天的数据
        today_data = self.data_manager.course_data[str(event.user_id)][str(current_weekday)]
        user_exact_time = self.data_manager.course_data[str(event.user_id)]["exact_time"]
        next_class = 0
        is_8 = 0
        try:
            row_num = get_driver().config.row_num
        except:
            row_num = 13
        for i in range(1, row_num + 1):
            for course in today_data[str(i)]:
                if current_week in course['week']:
                    msg += f"明天的第一节课为{course['name']},地点为{course['classroom']}\n,上课时间为{user_exact_time[str(i)]['start']}\n"
                    next_class = 1
                    if i == 1:
                        is_8 = 1
                    break
            if next_class == 1:
                break

        if next_class == 1:
            if is_8 == 1:
                msg = "明天有早八，记得早起捏\n" + msg
            else:
                msg = "明天没有早八，可以睡个懒觉捏\n" + msg
        else:
            msg = "明天没有课哦"

        weekday_info = ""
        if current_weekday == 1:
            weekday_info = "星期一"
        elif current_weekday == 2:
            weekday_info = "星期二"
        elif current_weekday == 3:
            weekday_info = "星期三"
        elif current_weekday == 4:
            weekday_info = "星期四"
        elif current_weekday == 5:
            weekday_info = "星期五"
        elif current_weekday == 6:
            weekday_info = "星期六"
        elif current_weekday == 7:
            weekday_info = "星期日"

        tmp = f"当前时间为{now_time},明天是第{current_week}周{weekday_info}\n"
        msg = tmp + msg
        return msg

    def get_exact_time(self, event):
        """
        获取用户上课时间
        :param event:
        :return:
        """
        self.init_user_data(event)
        user_id = str(event.user_id)
        return self.data_manager.course_data[user_id]['exact_time']


# 实例化
course_manager = CourseManager()
