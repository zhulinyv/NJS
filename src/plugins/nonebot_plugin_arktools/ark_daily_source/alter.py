"""如果无法截图"""
import time

WEEKDAYS = {
    "Mon": 1,
    "Tue": 2,
    "Wed": 3,
    "Thu": 4,
    "Fri": 5,
    "Sat": 6,
    "Sun": 7
}

SOURCE = {
    "作战记录(LS)": [1, 2, 3, 4, 5, 6, 7],
    "龙门币(CE)": [2, 4, 6, 7],
    "采购凭证(AP)": [1, 4, 6, 7],
    "碳素(SK)": [1, 3, 5, 6],
    "技巧概要(CA)": [2, 3, 5, 7],
    "医疗、重装芯片(PR-A)": [1, 4, 5, 7],
    "术师、狙击芯片(PR-B)": [1, 2, 5, 6],
    "辅助、先锋芯片(PR-C)": [3, 4, 6, 7],
    "特种、近卫芯片(PR-D)": [2, 3, 6, 7]
}


async def alter_plan():
    weekday = WEEKDAYS[time.strftime("%a", time.localtime())]
    return [name for name, day in SOURCE.items() if weekday in day]